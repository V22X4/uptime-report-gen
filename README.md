# Uptime Report Generator

---

## Requirements
- Python 3.8 or higher
- pip package manager

---

## Setup Instructions

Follow the steps below to set up and run the project locally:

1. **Clone the Repository**  
   ```bash
   git clone https://github.com/V22X4/uptime-report-gen.git
   ```
   Navigate into the project folder:  
   ```bash
   cd uptime-report-gen
   ```

2. **Set Up a Virtual Environment**  
   Create a new virtual environment:  
   ```bash
   python -m venv venv
   ```
   Activate the virtual environment:  
   - On **Windows**:  
     ```bash
     .\venv\Scripts\activate
     ```
   - On **macOS/Linux**:  
     ```bash
     source venv/bin/activate
     ```

3. **Install Dependencies**  
   Install the required Python packages:  
   ```bash
   pip install -r requirements.txt
   ```

4. **Prepare Data**  
   Copy the required CSV files (`store_status.csv`, `menu_hours.csv`, `timezones.csv`) into the `src/csv` directory.  
   Alternatively, download the demo data:  
   [Store Monitoring Data ZIP](https://storage.googleapis.com/hiring-problem-statements/store-monitoring-data.zip)  

   Extract the files and place them in the `src/csv` directory.

5. **Ingest Data**  
   Run the data ingestion script to load the data into the database:  
   ```bash
   python -m src.ingestion.ingestion
   ```
   **Note:** This step may take 5-6 minutes when using the demo files due to their large size.

6. **Run the Application**  
   Start the API server:  
   ```bash
   uvicorn src.api.routes:app --reload
   ```

---

## How to Use
1. After starting the server, access the API documentation at:  
   [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

2. Use the interactive Swagger UI to explore and test the endpoints.

---