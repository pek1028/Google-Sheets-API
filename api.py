from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from pydantic import BaseModel
from typing import List
import os

app = FastAPI(title="DOA")

# Google Sheets credentials
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'doa-selangor-e93913d5a942.json'
SPREADSHEET_ID = '1MGLfUVxUijs2ge7gWyY41eRtckCV-7twyik1zv85fOc'
SHEET_RANGE = 'Sheet1'

# Pydantic model for append data
class AppendData(BaseModel):
    values: List[List[str]]

# Initialize Google Sheets client
def get_sheets_service():
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        raise HTTPException(status_code=500, detail="Service account file not found")
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    return service

@app.get("/read", response_model=List[List[str]])
async def read_spreadsheet():
    """
    Read data from the Google Spreadsheet.
    Returns a list of rows, where each row is a list of cell values.
    """
    try:
        service = get_sheets_service()
        sheet = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=SHEET_RANGE
        ).execute()
        values = sheet.get('values', [])
        return values
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading spreadsheet: {str(e)}")

@app.post("/append", response_model=dict)
async def append_to_spreadsheet(data: AppendData):
    """
    Append data to the Google Spreadsheet.
    Expects a JSON body with a 'values' field containing a list of rows.
    """
    try:
        service = get_sheets_service()
        body = {'values': data.values}
        result = service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=SHEET_RANGE,
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body=body
        ).execute()
        return {
            "message": f"Appended {result.get('updates').get('updatedRows')} row(s)",
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error appending to spreadsheet: {str(e)}")