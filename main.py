from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import io

app = FastAPI()

# Frontend se connect hone ke liye CORS enable karein
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root route (Browser me test karne ke liye)
@app.get("/")
def read_root():
    return {"status": "success", "message": "Backend is running live on Railway!"}

@app.post("/analyze")
async def analyze_excel(file: UploadFile = File(...)):
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Sirf Excel (.xlsx, .xls) files allowed hain.")

    try:
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))

        # Core Calculations
        total_visits = int(df['School Name'].dropna().count())
        
        total_sampling = int((
            df['Samples']
            .astype(str)
            .str.strip()
            .str.lower() == 'drop'
        ).sum())

        total_adoptions = int((
            df['Adopted']
            .astype(str)
            .str.strip()
            .str.lower() == 'yes'
        ).sum())

        conversion_rate = round((total_adoptions / total_visits * 100), 2) if total_visits > 0 else 0.0

        return {
            "status": "success",
            "file_name": file.filename,
            "data": {
                "total_visits": total_visits,
                "total_sampling": total_sampling,
                "total_adoptions": total_adoptions,
                "conversion_rate": conversion_rate
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing Error: {str(e)}")