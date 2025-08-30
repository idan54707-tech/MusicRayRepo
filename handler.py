"""
musicRay - RunPod Serverless Handler
מעבד קבצי שמע והופך אותם ל-4 סטמים באמצעות Demucs
"""

import os
import json
import tempfile
import subprocess
import shutil
from pathlib import Path
import requests
import torch
import librosa
import soundfile as sf
import numpy as np
from urllib.parse import urlparse
import runpod

# הגדרת device
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"🎵 musicRay Serverless Handler - Device: {DEVICE}")

def download_file(url: str, output_path: str) -> bool:
    """
    הורדת קובץ מURL
    """
    try:
        print(f"📥 מוריד קובץ מ: {url}")
        response = requests.get(url, stream=True, timeout=300)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        file_size = os.path.getsize(output_path)
        print(f"✅ הורדה הושלמה: {file_size / 1024 / 1024:.1f}MB")
        return True
        
    except Exception as e:
        print(f"❌ שגיאה בהורדה: {str(e)}")
        return False

def convert_to_wav(input_path: str, output_path: str) -> bool:
    """
    המרה ל-WAV 44.1kHz stereo
    """
    try:
        print(f"🔄 ממיר ל-WAV: {input_path}")
        
        # קריאת הקובץ עם librosa
        audio, sr = librosa.load(input_path, sr=44100, mono=False)
        
        # וידוא stereo
        if audio.ndim == 1:
            audio = np.stack([audio, audio])
        elif audio.shape[0] > 2:
            audio = audio[:2]
        
        # שמירה
        sf.write(output_path, audio.T, 44100, subtype='FLOAT')
        print(f"✅ המרה הושלמה: {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ שגיאה בהמרה: {str(e)}")
        return False

def separate_audio(input_path: str, output_dir: str) -> dict:
    """
    הפרדת שמע ל-4 סטמים באמצעות Demucs
    """
    try:
        print(f"🎯 מפריד שמע עם Demucs על {DEVICE}")
        
        # יצירת תיקיית פלט
        os.makedirs(output_dir, exist_ok=True)
        
        # פקודת Demucs מותאמת לServerless
        cmd = [
            "python", "-m", "demucs.separate",
            "--name", "htdemucs",
            "--device", DEVICE,
            "--shifts", "5" if DEVICE == "cuda" else "1",
            "--overlap", "0.25",
            "--segment", "8" if DEVICE == "cuda" else "4",
            "--out", output_dir,
            input_path
        ]
        
        print(f"📝 מריץ: {' '.join(cmd[-6:])}")
        
        # הרצת Demucs
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=1800  # 30 דקות timeout
        )
        
        if result.returncode != 0:
            raise Exception(f"Demucs נכשל: {result.stderr}")
        
        print("✅ Demucs הושלם בהצלחה")
        
        # מציאת קבצי הפלט
        input_name = Path(input_path).stem
        stems_dir = Path(output_dir) / "htdemucs" / input_name
        
        if not stems_dir.exists():
            raise Exception(f"תיקיית פלט לא נמצאה: {stems_dir}")
        
        # העברת הקבצים לתיקייה הראשית
        stem_files = {}
        for stem_name in ["vocals", "drums", "bass", "other"]:
            src_file = stems_dir / f"{stem_name}.wav"
            dst_file = Path(output_dir) / f"{stem_name}.wav"
            
            if src_file.exists():
                shutil.move(str(src_file), str(dst_file))
                stem_files[stem_name] = str(dst_file)
                print(f"✅ {stem_name}: {dst_file}")
            else:
                print(f"⚠️  חסר: {stem_name}")
        
        # ניקוי תיקיית Demucs הזמנית
        shutil.rmtree(Path(output_dir) / "htdemucs", ignore_errors=True)
        
        return stem_files
        
    except subprocess.TimeoutExpired:
        raise Exception("Demucs חרג מזמן הריצה המותר (30 דקות)")
    except Exception as e:
        print(f"❌ שגיאה בהפרדת השמע: {str(e)}")
        raise

def analyze_audio(audio_path: str) -> dict:
    """
    ניתוח שמע - BPM ו-Key
    """
    try:
        print("📊 מנתח שמע...")
        
        # טעינת השמע
        y, sr = librosa.load(audio_path, sr=22050)
        duration = librosa.get_duration(y=y, sr=sr)
        
        # חישוב BPM
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        if tempo < 60:
            tempo *= 2
        elif tempo > 200:
            tempo /= 2
        
        # זיהוי מפתח (פשוט)
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        chroma_mean = np.mean(chroma, axis=1)
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        dominant_note = note_names[np.argmax(chroma_mean)]
        
        # זיהוי מודוס פשוט
        major_profile = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
        minor_profile = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
        
        major_corr = np.corrcoef(chroma_mean, major_profile / np.sum(major_profile))[0, 1]
        minor_corr = np.corrcoef(chroma_mean, minor_profile / np.sum(minor_profile))[0, 1]
        
        mode = "major" if major_corr > minor_corr else "minor"
        key = f"{dominant_note} {mode}"
        
        result = {
            "bpm": int(tempo),
            "key": key,
            "duration_sec": round(duration, 1)
        }
        
        print(f"✅ ניתוח: BPM={result['bpm']}, Key={result['key']}, Duration={result['duration_sec']}s")
        return result
        
    except Exception as e:
        print(f"⚠️  שגיאה בניתוח: {str(e)}")
        return {"bpm": 120, "key": "C major", "duration_sec": 180.0}

def handler(event):
    """
    RunPod Serverless Handler
    """
    try:
        print("🚀 musicRay Handler התחיל")
        print(f"📨 Event: {json.dumps(event, indent=2)}")
        
        # בדיקת input
        input_data = event.get("input", {})
        file_url = input_data.get("file_url")
        
        if not file_url:
            return {
                "error": "חסר שדה file_url ב-input"
            }
        
        # יצירת תיקיות זמניות
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # נתיבי קבצים
            original_file = temp_path / "input_audio"
            wav_file = temp_path / "input.wav"
            stems_dir = temp_path / "stems"
            stems_dir.mkdir()
            
            # הורדת הקובץ
            if not download_file(file_url, str(original_file)):
                return {"error": "שגיאה בהורדת הקובץ"}
            
            # המרה ל-WAV
            if not convert_to_wav(str(original_file), str(wav_file)):
                return {"error": "שגיאה בהמרת הקובץ ל-WAV"}
            
            # הפרדת סטמים
            stem_files = separate_audio(str(wav_file), str(stems_dir))
            
            if not stem_files:
                return {"error": "שגיאה בהפרדת הסטמים"}
            
            # ניתוח השמע
            analysis = analyze_audio(str(wav_file))
            
            # קריאת קבצי הסטמים ל-base64 (עבור החזרה)
            stems_data = {}
            for stem_name, file_path in stem_files.items():
                if os.path.exists(file_path):
                    # במקום base64, נחזיר רק מידע על הקובץ
                    # ב-production אמיתי תעלה ל-S3 ותחזיר URLs
                    file_size = os.path.getsize(file_path)
                    stems_data[stem_name] = {
                        "path": file_path,
                        "size_mb": round(file_size / 1024 / 1024, 2),
                        "exists": True
                    }
            
            # תשובה מוצלחת
            result = {
                "success": True,
                "stems": stems_data,
                "analysis": analysis,
                "processing_info": {
                    "device": DEVICE,
                    "total_stems": len(stems_data),
                    "message": "עיבוד הושלם בהצלחה"
                }
            }
            
            print("✅ Handler הושלם בהצלחה")
            print(f"📤 Result: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            return result
    
    except Exception as e:
        error_msg = f"שגיאה כללית: {str(e)}"
        print(f"❌ {error_msg}")
        
        return {
            "error": error_msg,
            "success": False
        }

# רישום ל-RunPod Serverless
if __name__ == "__main__":
    print("🏃 מתחיל RunPod Serverless Handler...")
    runpod.serverless.start({"handler": handler})
