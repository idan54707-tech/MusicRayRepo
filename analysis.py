import librosa
import numpy as np
from pathlib import Path
from typing import Tuple

async def analyze_audio(audio_path: Path) -> Tuple[float, str, float]:
    """
    ניתוח שמע לחישוב BPM, Key ומשך
    """
    try:
        print(f"מנתח קובץ שמע: {audio_path.name}")
        
        # טעינת השמע
        y, sr = librosa.load(str(audio_path), sr=22050)  # SR נמוך יותר לביצועים
        duration = librosa.get_duration(y=y, sr=sr)
        
        # חישוב BPM
        bpm = estimate_bpm(y, sr)
        
        # זיהוי מפתח מוזיקלי
        key = estimate_key(y, sr)
        
        print(f"ניתוח הושלם: BPM={bpm}, Key={key}, Duration={duration:.1f}s")
        return bpm, key, duration
        
    except Exception as e:
        print(f"שגיאה בניתוח השמע: {str(e)}")
        # ערכי ברירת מחדל במקרה של שגיאה
        return 120.0, "C major", 180.0

def estimate_bpm(y: np.ndarray, sr: int) -> float:
    """
    חישוב BPM באמצעות beat tracking
    """
    try:
        # חישוב onset strength
        onset_envelope = librosa.onset.onset_strength(y=y, sr=sr)
        
        # Beat tracking
        tempo, beats = librosa.beat.beat_track(
            onset_envelope=onset_envelope, 
            sr=sr,
            units='time'
        )
        
        # וידוא שה-BPM בטווח סביר
        if tempo < 60:
            tempo *= 2
        elif tempo > 200:
            tempo /= 2
        
        return float(tempo)
        
    except Exception as e:
        print(f"שגיאה בחישוב BPM: {str(e)}")
        return 120.0

def estimate_key(y: np.ndarray, sr: int) -> str:
    """
    זיהוי מפתח מוזיקלי באמצעות chromagram
    """
    try:
        # חישוב chromagram
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        
        # חישוב ממוצע על פני הזמן
        chroma_mean = np.mean(chroma, axis=1)
        
        # הגדרת שמות התווים
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        
        # מציאת התו הדומיננטי
        dominant_note_idx = np.argmax(chroma_mean)
        dominant_note = note_names[dominant_note_idx]
        
        # זיהוי מודוס (major/minor) - אלגוריתם פשוט
        mode = estimate_mode(chroma_mean)
        
        return f"{dominant_note} {mode}"
        
    except Exception as e:
        print(f"שגיאה בזיהוי מפתח: {str(e)}")
        return "C major"

def estimate_mode(chroma_profile: np.ndarray) -> str:
    """
    זיהוי מודוס (major/minor) על בסיס פרופיל כרומטי
    """
    try:
        # פרופילי major ו-minor (Krumhansl-Schmuckler)
        major_profile = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
        minor_profile = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
        
        # נורמליזציה
        major_profile = major_profile / np.sum(major_profile)
        minor_profile = minor_profile / np.sum(minor_profile)
        chroma_norm = chroma_profile / np.sum(chroma_profile)
        
        # חישוב correlation
        major_corr = np.corrcoef(chroma_norm, major_profile)[0, 1]
        minor_corr = np.corrcoef(chroma_norm, minor_profile)[0, 1]
        
        # החזרת המודוס עם הcorrelation הגבוה יותר
        return "major" if major_corr > minor_corr else "minor"
        
    except Exception as e:
        print(f"שגיאה בזיהוי מודוס: {str(e)}")
        return "major"

def analyze_harmonic_content(y: np.ndarray, sr: int) -> dict:
    """
    ניתוח הרמוני מתקדם (לעתיד)
    """
    try:
        # TODO: הוספת ניתוח אקורדים ופרוגרסיות הרמוניות
        # באמצעות Essentia או Chordino
        
        return {
            "chords": [],
            "progressions": [],
            "harmonic_rhythm": 4.0
        }
        
    except Exception as e:
        print(f"שגיאה בניתוח הרמוני: {str(e)}")
        return {}
