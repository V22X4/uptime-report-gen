import os
import pandas as pd
from sqlalchemy.orm import Session
from zipfile import ZipFile
from datetime import datetime
from src.models import StoreStatus, BusinessHours, StoreTimezone, Base
from src.db import engine, get_db

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

# Paths and constants
ZIP_FILE_URL = "https://storage.googleapis.com/hiring-problem-statements/store-monitoring-data.zip"
CSV_FILES = ["store_status.csv", "menu_hours.csv", "timezones.csv"]
DEFAULT_TIMEZONE = "America/Chicago"


# Function to load CSVs into dataframes
def load_csv_to_dataframe(file_path, **kwargs):
    return pd.read_csv(file_path, **kwargs)

# Insert data into StoreStatus table
from datetime import datetime

def insert_store_status(data, db: Session):
    for _, row in data.iterrows():
        timestamp_str = row['timestamp_utc']
        # Remove timezone info (if always "UTC") and parse microseconds
        if "UTC" in timestamp_str:
            timestamp_str = timestamp_str.replace(" UTC", "")
        # Use format with microseconds
        timestamp_utc = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S.%f")
        db.add(StoreStatus(
            store_id=row['store_id'],
            timestamp_utc=timestamp_utc,
            status=row['status']
        ))
    db.commit()


# Insert data into BusinessHours table
def insert_business_hours(data, db: Session):
    for _, row in data.iterrows():
        db.add(BusinessHours(
            store_id=row['store_id'],
            day_of_week=row['dayOfWeek'],
            start_time_local=row['start_time_local'],
            end_time_local=row['end_time_local']
        ))
    db.commit()

# Insert data into StoreTimezone table
def insert_store_timezones(data, db: Session):
    for _, row in data.iterrows():
        db.add(StoreTimezone(
            store_id=row['store_id'],
            timezone_str=row.get('timezone_str', DEFAULT_TIMEZONE)
        ))
    db.commit()

def main(folder_path):
    with get_db() as db:
        # Process store_status.csv
        status_file = os.path.join(folder_path, "store_status.csv")
        
        if os.path.exists(status_file):
            status_data = load_csv_to_dataframe(status_file)
            insert_store_status(status_data, db)
        
        # Process menu_hours.csv
        hours_file = os.path.join(folder_path, "menu_hours.csv")
        if os.path.exists(hours_file):
            hours_data = load_csv_to_dataframe(hours_file)
            insert_business_hours(hours_data, db)
        
        # Process timezones.csv
        timezones_file = os.path.join(folder_path, "timezones.csv")
        if os.path.exists(timezones_file):
            timezones_data = load_csv_to_dataframe(timezones_file)
            insert_store_timezones(timezones_data, db)

    print("Data successfully inserted into the database.")
    

if __name__ == "__main__":
    # Ensure you have downloaded the zip file manually or replace the path with a downloaded path
    if __name__ == "__main__":
        folder_path = "./src/csv"
    main(folder_path)
