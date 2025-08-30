#!/usr/bin/env python3
"""
בדיקת Handler מקומית לפני העלאה ל-RunPod Serverless
"""

import json
from handler import handler

def test_handler_local():
    """
    בדיקת Handler עם קובץ מקומי
    """
    import os
    from pathlib import Path
    
    # יצירת קובץ דוגמה אם לא קיים
    test_audio_path = Path("test_audio.wav")
    if not test_audio_path.exists():
        print("🎵 יוצר קובץ דוגמה...")
        import numpy as np
        import soundfile as sf
        sr = 44100
        t = np.linspace(0, 5, sr*5)  # 5 שניות
        audio = np.sin(2*np.pi*440*t)  # 440Hz (A4)
        sf.write(str(test_audio_path), audio, sr)
    
    # בדיקה ישירה עם קובץ מקומי
    print("🧪 בודק Handler מקומית עם קובץ מקומי...")
    
    try:
        # קריאה ישירה לפונקציות הפנימיות
        from handler import convert_to_wav, separate_audio, analyze_audio
        import tempfile
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            wav_file = temp_path / "input.wav"
            stems_dir = temp_path / "stems"
            stems_dir.mkdir()
            
            print(f"🔄 ממיר ל-WAV...")
            if not convert_to_wav(str(test_audio_path), str(wav_file)):
                print("❌ המרה נכשלה")
                return
            
            print(f"🎯 מפריד סטמים...")
            stem_files = separate_audio(str(wav_file), str(stems_dir))
            
            print(f"📊 מנתח שמע...")
            analysis = analyze_audio(str(wav_file))
            
            print("✅ בדיקה הושלמה בהצלחה!")
            print(f"🎵 סטמים שנוצרו: {list(stem_files.keys())}")
            print(f"📊 ניתוח: {analysis}")
            
    except Exception as e:
        print(f"❌ שגיאה: {str(e)}")
        import traceback
        traceback.print_exc()

def test_handler():
    """
    בדיקת Handler עם URL (אם יש אינטרנט)
    """
    
    # דוגמת event - קובץ קטן לבדיקה
    test_event = {
        "input": {
            "file_url": "https://www2.cs.uic.edu/~i101/SoundFiles/BabyElephantWalk60.wav"  # קובץ דוגמה קטן ~60 שניות
        }
    }
    
    print("🧪 בודק Handler מקומית...")
    print(f"📨 Test Event: {json.dumps(test_event, indent=2)}")
    
    try:
        # הרצת Handler
        result = handler(test_event)
        
        print("\n📤 תוצאה:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # בדיקת תוצאה
        if result.get("success"):
            print("\n✅ בדיקה עברה בהצלחה!")
            stems = result.get("stems", {})
            print(f"🎵 נוצרו {len(stems)} סטמים:")
            for stem_name, info in stems.items():
                print(f"  - {stem_name}: {info.get('size_mb', 0)}MB")
        else:
            print(f"\n❌ בדיקה נכשלה: {result.get('error', 'שגיאה לא ידועה')}")
            
    except Exception as e:
        print(f"\n💥 שגיאה בהרצת Handler: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 בדיקת musicRay Serverless Handler")
    print("=" * 50)
    
    # בדיקה מקומית (מהירה)
    test_handler_local()
