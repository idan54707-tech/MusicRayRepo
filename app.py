import os
import uuid
import shutil
from pathlib import Path
from typing import Dict, Any
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import torch

from separate import separate_audio
from postprocess import postprocess_stems
from analysis import analyze_audio

# זיהוי סביבת הרצה
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
IS_RUNPOD = os.getenv("RUNPOD_POD_ID") is not None
IS_CLOUD = IS_RUNPOD or os.getenv("CLOUD_PROVIDER") is not None

print(f"🚀 musicRay מתחיל...")
print(f"📱 Device: {DEVICE}")
print(f"☁️  Cloud: {IS_CLOUD}")
if IS_RUNPOD:
    print(f"🏃 RunPod Pod ID: {os.getenv('RUNPOD_POD_ID')}")
if DEVICE == "cuda":
    print(f"🎮 GPU: {torch.cuda.get_device_name()}")
    print(f"💾 GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f}GB")

# הגבלות קלט - מותאמות לסביבה
if IS_CLOUD:
    MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB בענן
    MAX_DURATION = 20 * 60  # 20 דקות בענן
    CORS_ORIGINS = ["*"]  # פתוח בענן
else:
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB מקומי
    MAX_DURATION = 10 * 60  # 10 דקות מקומי
    CORS_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000"]

app = FastAPI(title="musicRay API", version="1.0.0")

# הגדרת CORS לחיבור עם Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# יצירת תיקיית storage
STORAGE_DIR = Path("storage")
STORAGE_DIR.mkdir(exist_ok=True)

@app.post("/upload")
async def upload_audio(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    העלאת קובץ שמע והפרדה לסטמים
    """
    try:
        # בדיקת גודל קובץ
        contents = await file.read()
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="הקובץ גדול מדי (מקסימום 100MB)")
        
        # בדיקת סוג קובץ
        if not file.filename or not file.filename.lower().endswith(('.mp3', '.wav', '.flac', '.m4a')):
            raise HTTPException(status_code=400, detail="פורמט קובץ לא נתמך. השתמש ב-MP3, WAV, FLAC או M4A")
        
        # יצירת job_id ייחודי
        job_id = str(uuid.uuid4())
        job_dir = STORAGE_DIR / job_id
        job_dir.mkdir(exist_ok=True)
        
        # שמירת הקובץ המקורי
        input_path = job_dir / f"input{Path(file.filename).suffix}"
        with open(input_path, "wb") as f:
            f.write(contents)
        
        print(f"מתחיל עיבוד job {job_id} עבור קובץ {file.filename}")
        
        # המרה ל-WAV והפרדה
        stems_paths = await separate_audio(input_path, job_dir)
        
        # Post-processing לכל סטם
        processed_stems = await postprocess_stems(stems_paths)
        
        # ניתוח BPM ו-Key
        bpm, key, duration = await analyze_audio(input_path)
        
        # בדיקת משך השיר
        if duration > MAX_DURATION:
            # נקה קבצים ותחזיר שגיאה
            shutil.rmtree(job_dir, ignore_errors=True)
            raise HTTPException(status_code=413, detail=f"השיר ארוך מדי ({duration/60:.1f} דקות). מקסימום 10 דקות")
        
        # הכנת התשובה
        response = {
            "job_id": job_id,
            "stems": {
                "vocals": f"/files/{job_id}/vocals.wav",
                "drums": f"/files/{job_id}/drums.wav", 
                "bass": f"/files/{job_id}/bass.wav",
                "other": f"/files/{job_id}/other.wav"
            },
            "bpm": int(bpm),
            "key": key,
            "duration_sec": round(duration, 1)
        }
        
        print(f"הושלם עיבוד job {job_id}: BPM={bpm}, Key={key}, Duration={duration:.1f}s")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"שגיאה בעיבוד: {str(e)}")
        # ניקוי במקרה של שגיאה
        if 'job_dir' in locals():
            shutil.rmtree(job_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail=f"שגיאה בעיבוד השיר: {str(e)}")

@app.get("/files/{job_id}/{filename}")
async def get_file(job_id: str, filename: str):
    """
    הורדת קובץ סטם
    """
    try:
        file_path = STORAGE_DIR / job_id / filename
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="הקובץ לא נמצא")
        
        return FileResponse(
            path=str(file_path),
            media_type="audio/wav",
            filename=filename
        )
    except Exception as e:
        print(f"שגיאה בהורדת קובץ {job_id}/{filename}: {str(e)}")
        raise HTTPException(status_code=500, detail="שגיאה בהורדת הקובץ")

@app.delete("/files/{job_id}")
async def delete_job(job_id: str):
    """
    מחיקת כל קבצי ה-job
    """
    try:
        job_dir = STORAGE_DIR / job_id
        if job_dir.exists():
            shutil.rmtree(job_dir)
            return {"message": f"נמחקו כל קבצי job {job_id}"}
        else:
            raise HTTPException(status_code=404, detail="Job לא נמצא")
    except HTTPException:
        raise
    except Exception as e:
        print(f"שגיאה במחיקת job {job_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="שגיאה במחיקת הקבצים")

@app.get("/health")
async def health_check():
    """
    בדיקת תקינות השרת
    """
    return {"status": "healthy", "message": "musicRay API פועל בהצלחה"}

@app.get("/system-info")
async def system_info():
    """
    מידע על המערכת והביצועים
    """
    gpu_info = {}
    if DEVICE == "cuda":
        gpu_info = {
            "gpu_name": torch.cuda.get_device_name(),
            "gpu_memory_total": f"{torch.cuda.get_device_properties(0).total_memory / 1e9:.1f}GB",
            "gpu_memory_available": f"{torch.cuda.get_device_properties(0).total_memory / 1e9:.1f}GB"
        }
    
    return {
        "device": DEVICE,
        "is_cloud": IS_CLOUD,
        "is_runpod": IS_RUNPOD,
        "max_file_size_mb": MAX_FILE_SIZE // (1024 * 1024),
        "max_duration_minutes": MAX_DURATION // 60,
        "gpu_info": gpu_info,
        "performance_tier": "high" if DEVICE == "cuda" else "standard"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
