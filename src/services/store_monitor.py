from datetime import datetime, timedelta
import pytz
from typing import Dict, List, Optional, Tuple
import pandas as pd
from sqlalchemy.orm import Session

from src.models.db_models import StoreStatus, BusinessHours, StoreTimezone
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def get_local_time(utc_time: datetime, timezone_str: str) -> datetime:
    tz = pytz.timezone(timezone_str)
    return utc_time.astimezone(tz)

def is_within_business_hours(
    time: datetime, 
    business_hours: List[BusinessHours]
) -> bool:
    day_of_week = time.weekday()
    time_str = time.strftime("%H:%M:%S")
    
    day_hours = [bh for bh in business_hours if bh.day_of_week == day_of_week]
    if not day_hours:
        return True
        
    for hours in day_hours:
        if hours.start_time_local <= time_str <= hours.end_time_local:
            return True
    return False

def interpolate_status(
    observations: List[Tuple[datetime, str]], 
    interval_start: datetime,
    interval_end: datetime
) -> Tuple[float, float]:
    if not observations:
        return 0, 0
        
    uptime = downtime = 0
    prev_time = None
    prev_status = None
    
    if observations[0][0] > interval_start:
        observations.insert(0, (interval_start, observations[0][1]))
    if observations[-1][0] < interval_end:
        observations.append((interval_end, observations[-1][1]))
    
    for curr_time, curr_status in observations:
        if prev_time is not None:
            duration = (curr_time - prev_time).total_seconds() / 3600
            if prev_status == "active":
                uptime += duration
            else:
                downtime += duration
        
        prev_time = curr_time
        prev_status = curr_status
    
    return uptime, downtime

class StoreMonitor:
    def __init__(self, db: Session):
        self.db = db
        self.logger = setup_logger(__name__)
    
    def get_store_timezone(self, store_id: int) -> str:
        timezone = self.db.query(StoreTimezone).filter_by(store_id=store_id).first()
        return timezone.timezone_str if timezone else "America/Chicago"
    
    def get_business_hours(self, store_id: int) -> List[BusinessHours]:
        hours = self.db.query(BusinessHours).filter_by(store_id=store_id).all()
        if not hours:
            hours = []
            for day in range(7):
                hours.append(BusinessHours(
                    store_id=store_id,
                    day_of_week=day,
                    start_time_local="00:00:00",
                    end_time_local="23:59:59"
                ))
        return hours
    
    def compute_store_metrics(
        self, 
        store_id: int,
        current_time: datetime
    ) -> Dict[str, float]:
        try:
            timezone_str = self.get_store_timezone(store_id)
            business_hours = self.get_business_hours(store_id)
            
            intervals = {
                "hour": current_time - timedelta(hours=1),
                "day": current_time - timedelta(days=1),
                "week": current_time - timedelta(weeks=1)
            }
            
            metrics = {
                "uptime_last_hour": 0,
                "uptime_last_day": 0,
                "uptime_last_week": 0,
                "downtime_last_hour": 0,
                "downtime_last_day": 0,
                "downtime_last_week": 0
            }
            
            for interval_name, start_time in intervals.items():
                observations = (
                    self.db.query(StoreStatus)
                    .filter(
                        StoreStatus.store_id == store_id,
                        StoreStatus.timestamp_utc.between(start_time, current_time)
                    )
                    .order_by(StoreStatus.timestamp_utc)
                    .all()
                )
                
                business_hours_obs = []
                for obs in observations:
                    local_time = get_local_time(obs.timestamp_utc, timezone_str)
                    if is_within_business_hours(local_time, business_hours):
                        business_hours_obs.append(
                            (obs.timestamp_utc, obs.status)
                        )
                
                uptime, downtime = interpolate_status(
                    business_hours_obs,
                    start_time,
                    current_time
                )
                
                if interval_name == "hour":
                    metrics[f"uptime_last_{interval_name}"] = round(uptime * 60, 2)
                    metrics[f"downtime_last_{interval_name}"] = round(downtime * 60, 2)
                else:
                    metrics[f"uptime_last_{interval_name}"] = round(uptime, 2)
                    metrics[f"downtime_last_{interval_name}"] = round(downtime, 2)
            
            return metrics
            
        except Exception as e:
            self.logger.error(
                f"Error computing metrics for store {store_id}: {str(e)}"
            )
            raise
