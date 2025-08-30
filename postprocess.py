import numpy as np
import librosa
import soundfile as sf
from pathlib import Path
from typing import Dict, Tuple
import scipy.signal

async def postprocess_stems(stems_paths: Dict[str, Path]) -> Dict[str, Path]:
    """
    עיבוד מתקדם של כל הסטמים לשיפור איכות
    """
    processed_paths = {}
    
    try:
        for stem_name, path in stems_paths.items():
            print(f"מעבד סטם: {stem_name}")
            processed_path = await process_single_stem(path, stem_name)
            processed_paths[stem_name] = processed_path
        
        print(f"Post-processing הושלם עבור {len(processed_paths)} סטמים")
        return processed_paths
        
    except Exception as e:
        print(f"שגיאה ב-post-processing: {str(e)}")
        raise

async def process_single_stem(input_path: Path, stem_type: str) -> Path:
    """
    עיבוד סטם יחיד
    """
    try:
        # קריאת הקובץ
        audio, sr = librosa.load(str(input_path), sr=44100, mono=False)
        
        # וידוא שהשמע הוא stereo
        if audio.ndim == 1:
            audio = np.stack([audio, audio])
        
        # שלב 1: Loudness Normalization ל--14 LUFS
        audio = normalize_loudness(audio, sr)
        
        # שלב 2: סינון תדרים לפי סוג הסטם
        audio = apply_frequency_filtering(audio, sr, stem_type)
        
        # שלב 3: Denoise עדין
        audio = gentle_denoise(audio, sr)
        
        # שלב 4: Phase Alignment
        audio = phase_alignment(audio)
        
        # שלב 5: Fade-in/out ו-Trimming
        audio = apply_fades(audio, sr)
        
        # שמירת הקובץ המעובד
        output_path = input_path.parent / f"{stem_type}_processed.wav"
        sf.write(str(output_path), audio.T, sr, subtype='FLOAT')
        
        # החלפת הקובץ המקורי
        input_path.unlink()  # מחיקת המקורי
        output_path.rename(input_path)  # שינוי שם המעובד
        
        return input_path
        
    except Exception as e:
        print(f"שגיאה בעיבוד סטם {stem_type}: {str(e)}")
        raise

def normalize_loudness(audio: np.ndarray, sr: int, target_lufs: float = -14.0) -> np.ndarray:
    """
    נורמליזציה של עוצמת השמע ל-LUFS מטרה
    """
    try:
        # חישוב RMS נוכחי
        rms = np.sqrt(np.mean(audio**2))
        
        if rms < 1e-6:  # שמע שקט מדי
            return audio
        
        # חישוב gain נדרש (קירוב פשוט ל-LUFS)
        current_db = 20 * np.log10(rms)
        target_db = target_lufs + 23  # המרה קרובה מ-LUFS ל-dB
        gain_db = target_db - current_db
        
        # הגבלת gain
        gain_db = np.clip(gain_db, -20, 20)
        gain_linear = 10**(gain_db / 20)
        
        normalized = audio * gain_linear
        
        # וידוא שאין clipping
        peak = np.max(np.abs(normalized))
        if peak > 0.95:
            normalized = normalized * (0.95 / peak)
        
        return normalized
        
    except Exception as e:
        print(f"שגיאה בנורמליזציה: {str(e)}")
        return audio

def apply_frequency_filtering(audio: np.ndarray, sr: int, stem_type: str) -> np.ndarray:
    """
    סינון תדרים עדין לפי סוג הסטם
    """
    try:
        if stem_type == "vocals":
            # HPF ב-80Hz לווקלס
            audio = apply_highpass_filter(audio, sr, 80, order=2)
        elif stem_type == "bass":
            # LPF ב-8kHz לבס
            audio = apply_lowpass_filter(audio, sr, 8000, order=2)
        elif stem_type == "drums":
            # HPF עדין ב-30Hz לתופים
            audio = apply_highpass_filter(audio, sr, 30, order=1)
        # "other" - ללא סינון מיוחד
        
        return audio
        
    except Exception as e:
        print(f"שגיאה בסינון תדרים עבור {stem_type}: {str(e)}")
        return audio

def apply_highpass_filter(audio: np.ndarray, sr: int, cutoff: float, order: int = 2) -> np.ndarray:
    """
    מסנן עליון (HPF)
    """
    try:
        nyquist = sr / 2
        normalized_cutoff = cutoff / nyquist
        b, a = scipy.signal.butter(order, normalized_cutoff, btype='high')
        
        filtered = np.zeros_like(audio)
        for ch in range(audio.shape[0]):
            filtered[ch] = scipy.signal.filtfilt(b, a, audio[ch])
        
        return filtered
    except:
        return audio

def apply_lowpass_filter(audio: np.ndarray, sr: int, cutoff: float, order: int = 2) -> np.ndarray:
    """
    מסנן תחתון (LPF) 
    """
    try:
        nyquist = sr / 2
        normalized_cutoff = cutoff / nyquist
        b, a = scipy.signal.butter(order, normalized_cutoff, btype='low')
        
        filtered = np.zeros_like(audio)
        for ch in range(audio.shape[0]):
            filtered[ch] = scipy.signal.filtfilt(b, a, audio[ch])
        
        return filtered
    except:
        return audio

def gentle_denoise(audio: np.ndarray, sr: int) -> np.ndarray:
    """
    הפחתת רעש עדינה
    """
    try:
        # חישוב RMS
        rms = np.sqrt(np.mean(audio**2))
        
        # אם השמע שקט מדי, החל noise gate עדין
        if rms < 0.01:  # threshold נמוך
            gate_threshold = rms * 0.1
            mask = np.abs(audio) > gate_threshold
            audio = audio * mask
        
        return audio
        
    except Exception as e:
        print(f"שגיאה ב-denoising: {str(e)}")
        return audio

def phase_alignment(audio: np.ndarray) -> np.ndarray:
    """
    יישור פאזה בין ערוצי סטריאו
    """
    try:
        if audio.shape[0] != 2:
            return audio
        
        # חישוב cross-correlation בין הערוצים
        correlation = np.correlate(audio[0][:1000], audio[1][:1000], mode='full')
        delay = np.argmax(correlation) - len(audio[1][:1000]) + 1
        
        # תיקון עיכוב קטן בלבד (עד 10 samples)
        if abs(delay) <= 10 and delay != 0:
            if delay > 0:
                audio[1] = np.roll(audio[1], delay)
            else:
                audio[0] = np.roll(audio[0], -delay)
        
        return audio
        
    except Exception as e:
        print(f"שגיאה ביישור פאזה: {str(e)}")
        return audio

def apply_fades(audio: np.ndarray, sr: int) -> np.ndarray:
    """
    החלת fade-in/out למניעת clicks
    """
    try:
        fade_samples = int(0.01 * sr)  # 10ms
        
        if audio.shape[1] > fade_samples * 2:
            # Fade-in
            fade_in = np.linspace(0, 1, fade_samples)
            for ch in range(audio.shape[0]):
                audio[ch][:fade_samples] *= fade_in
            
            # Fade-out
            fade_out = np.linspace(1, 0, fade_samples)
            for ch in range(audio.shape[0]):
                audio[ch][-fade_samples:] *= fade_out
        
        return audio
        
    except Exception as e:
        print(f"שגיאה ב-fades: {str(e)}")
        return audio
