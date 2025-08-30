import os
import subprocess
import shutil
from pathlib import Path
from typing import Dict
import soundfile as sf
import librosa
import numpy as np
import torch

# זיהוי device
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
IS_RUNPOD = os.getenv("RUNPOD_POD_ID") is not None

async def separate_audio(input_path: Path, output_dir: Path) -> Dict[str, Path]:
    """
    הפרדת שמע לסטמים באמצעות Demucs
    """
    try:
        # המרה ל-WAV 44.1kHz stereo אם נדרש
        wav_path = await convert_to_wav(input_path, output_dir)
        
        # הרצת Demucs עם פרמטרים איכותיים
        stems_dir = await run_demucs_separation(wav_path, output_dir)
        
        # החזרת נתיבי הסטמים
        stems_paths = {
            "vocals": stems_dir / "vocals.wav",
            "drums": stems_dir / "drums.wav", 
            "bass": stems_dir / "bass.wav",
            "other": stems_dir / "other.wav"
        }
        
        # וידוא שכל הקבצים נוצרו
        for stem_name, path in stems_paths.items():
            if not path.exists():
                raise Exception(f"סטם {stem_name} לא נוצר בהצלחה")
        
        print(f"הפרדה הושלמה בהצלחה: {len(stems_paths)} סטמים")
        return stems_paths
        
    except Exception as e:
        print(f"שגיאה בהפרדת השמע: {str(e)}")
        raise

async def convert_to_wav(input_path: Path, output_dir: Path) -> Path:
    """
    המרה ל-WAV 44.1kHz stereo
    """
    output_path = output_dir / "input_converted.wav"
    
    try:
        # קריאת הקובץ המקורי
        audio, sr = librosa.load(str(input_path), sr=44100, mono=False)
        
        # וידוא שהשמע הוא stereo
        if audio.ndim == 1:
            # המרה ממונו לסטריאו
            audio = np.stack([audio, audio])
        elif audio.shape[0] > 2:
            # אם יש יותר מ-2 ערוצים, קח את הראשונים
            audio = audio[:2]
        
        # שמירה כ-WAV
        sf.write(str(output_path), audio.T, 44100, subtype='FLOAT')
        
        print(f"המרה הושלמה: {input_path.name} -> {output_path.name}")
        return output_path
        
    except Exception as e:
        print(f"שגיאה בהמרת הקובץ: {str(e)}")
        raise

async def run_demucs_separation(wav_path: Path, output_dir: Path) -> Path:
    """
    הרצת Demucs להפרדת סטמים
    """
    try:
        # יצירת תיקיית פלט זמנית
        temp_output = output_dir / "demucs_output"
        temp_output.mkdir(exist_ok=True)
        
        # פקודת Demucs עם פרמטרים מותאמים לסביבה
        cmd = [
            "python", "-m", "demucs.separate",
            "--name", "htdemucs",  # מודל איכותי
            "--device", DEVICE,    # GPU או CPU
            "--out", str(temp_output),
            str(wav_path)
        ]
        
        # פרמטרים איכותיים לGPU או מהירים לCPU
        if DEVICE == "cuda" or IS_RUNPOD:
            cmd.extend([
                "--shifts", "5",       # איכות גבוהה
                "--overlap", "0.25",   # חפיפה טובה
                "--segment", "8",      # פלחים גדולים יותר לGPU
            ])
            print(f"🎮 מריץ Demucs על GPU באיכות גבוהה")
        else:
            cmd.extend([
                "--shifts", "1",       # מהיר יותר
                "--overlap", "0.1",    # פחות חפיפה
                "--segment", "4",      # פלחים קטנים לCPU
            ])
            print(f"💻 מריץ Demucs על CPU במהירות")
        
        print(f"📝 פקודה: {' '.join(cmd[-8:])}")  # הדפס רק חלק מהפקודה
        
        # הרצת הפקודה
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=1800  # timeout של 30 דקות
        )
        
        if result.returncode != 0:
            raise Exception(f"Demucs נכשל: {result.stderr}")
        
        print("Demucs הושלם בהצלחה")
        
        # מציאת תיקיית הפלט של Demucs
        model_output_dir = temp_output / "htdemucs" / wav_path.stem
        if not model_output_dir.exists():
            raise Exception("תיקיית פלט של Demucs לא נמצאה")
        
        # העברת הקבצים למקום הסופי
        final_stems_dir = output_dir
        stem_mapping = {
            "vocals.wav": "vocals.wav",
            "drums.wav": "drums.wav",
            "bass.wav": "bass.wav", 
            "other.wav": "other.wav"
        }
        
        for demucs_name, final_name in stem_mapping.items():
            src = model_output_dir / demucs_name
            dst = final_stems_dir / final_name
            
            if src.exists():
                shutil.copy2(src, dst)
                print(f"הועבר: {demucs_name} -> {final_name}")
            else:
                print(f"אזהרה: קובץ {demucs_name} לא נמצא")
        
        # ניקוי תיקיית הזמנית
        shutil.rmtree(temp_output, ignore_errors=True)
        
        return final_stems_dir
        
    except subprocess.TimeoutExpired:
        print("Demucs חרג מזמן הריצה המותר")
        raise Exception("עיבוד השיר ארך זמן רב מדי")
    except Exception as e:
        print(f"שגיאה בהרצת Demucs: {str(e)}")
        raise

async def run_uvr_enhancement(vocals_path: Path, mix_path: Path, output_dir: Path) -> Path:
    """
    שיפור אופציונלי עם UVR-MDX-Net (לעתיד)
    כרגע מחזיר את הקובץ המקורי
    """
    # TODO: הוספת UVR-MDX-Net integration
    return vocals_path
