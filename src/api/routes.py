import os
import uuid
from datetime import datetime
import csv
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse

from src.db.database import get_db
from src.models.db_models import Report
from src.services.store_monitor import StoreMonitor
from src.utils.logger import setup_logger
from src.models.db_models import StoreStatus

app = FastAPI()
logger = setup_logger(__name__)

async def generate_report(report_id: str):
    try:
        with get_db() as db:
        
            result = (
                db.query(StoreStatus.timestamp_utc)
                .order_by(StoreStatus.timestamp_utc.desc())
                .first()
            )

            if result is None:
                print("No data available for report")

            current_time = result[0]
            
            store_ids = (
                db.query(StoreStatus.store_id)
                .distinct()
                .all()
            )
            
            monitor = StoreMonitor(db)
            
            os.makedirs("reports", exist_ok=True)
            file_path = f"reports/{report_id}.csv"
            
            # print("Writing report to", file_path)
            
            with open(file_path, "w", newline="") as f:
                print("Writing report to", file_path)
                writer = csv.writer(f)
                writer.writerow([
                    "store_id",
                    "uptime_last_hour",
                    "uptime_last_day",
                    "uptime_last_week",
                    "downtime_last_hour",
                    "downtime_last_day",
                    "downtime_last_week"
                ])
                
                for (store_id,) in store_ids:
                    metrics = monitor.compute_store_metrics(
                        store_id, 
                        current_time
                    )
                    writer.writerow([
                        store_id,
                        metrics["uptime_last_hour"],
                        metrics["uptime_last_day"],
                        metrics["uptime_last_week"],
                        metrics["downtime_last_hour"],
                        metrics["downtime_last_day"],
                        metrics["downtime_last_week"]
                    ])
            
            report = db.query(Report).filter_by(id=report_id).first()
            report.status = "Complete"
            report.completed_at = datetime.utcnow()
            report.file_path = file_path
            db.commit()
            
    except Exception as e:
        logger.error(f"Error generating report {report_id}: {str(e)}")
        with get_db() as db:
            report = db.query(Report).filter_by(id=report_id).first()
            report.status = "Failed"
            db.commit()

@app.post("/trigger_report")
async def trigger_report(background_tasks: BackgroundTasks):
    try:
        report_id = str(uuid.uuid4())
        with get_db() as db:
            report = Report(
                id=report_id,
                status="Running",
                created_at=datetime.now()
            )
            
            db.add(report) 
            db.commit()
            
        background_tasks.add_task(generate_report, report_id)
        return {"report_id": report_id}
        
    except Exception as e:
        logger.error(f"Error triggering report: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to trigger report generation"
        )

@app.get("/get_report/{report_id}")
async def get_report(report_id: str):
    try:
        with get_db() as db:
            report = db.query(Report).filter_by(id=report_id).first()
            
            if not report:
                raise HTTPException(
                    status_code=404,
                    detail="Report not found"
                )
            
            if report.status == "Running":
                return {"status": "Running"}
            elif report.status == "Failed":
                return {"status": "Failed"}
            
            return FileResponse(
                path=report.file_path,
                media_type="text/csv",
                filename=f"report_{report_id}.csv"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving report {report_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve report"
        )
