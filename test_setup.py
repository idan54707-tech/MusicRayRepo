#!/usr/bin/env python3
"""
בדיקת תקינות הגדרת המערכת עבור musicRay
"""

import sys
import subprocess
import importlib.util

def check_python_version():
    """בדיקת גרסת Python"""
    version = sys.version_info
    print(f"🐍 Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ נדרש")
        return False
    else:
        print("✅ גרסת Python תקינה")
        return True

def check_package(package_name, import_name=None):
    """בדיקת חבילה"""
    if import_name is None:
        import_name = package_name
    
    try:
        spec = importlib.util.find_spec(import_name)
        if spec is None:
            print(f"❌ {package_name} לא מותקן")
            return False
        else:
            try:
                module = importlib.import_module(import_name)
                version = getattr(module, '__version__', 'unknown')
                print(f"✅ {package_name} ({version})")
                return True
            except Exception as e:
                print(f"⚠️  {package_name} מותקן אבל יש בעיה: {e}")
                return False
    except Exception as e:
        print(f"❌ בעיה בבדיקת {package_name}: {e}")
        return False

def check_ffmpeg():
    """בדיקת ffmpeg"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"✅ {version_line}")
            return True
        else:
            print("❌ ffmpeg לא עובד כראוי")
            return False
    except FileNotFoundError:
        print("❌ ffmpeg לא מותקן או לא נמצא ב-PATH")
        print("   התקן מ-https://ffmpeg.org/download.html")
        return False
    except subprocess.TimeoutExpired:
        print("❌ ffmpeg לא מגיב")
        return False
    except Exception as e:
        print(f"❌ בעיה בבדיקת ffmpeg: {e}")
        return False

def check_torch_cuda():
    """בדיקת PyTorch ו-CUDA"""
    try:
        import torch
        print(f"✅ PyTorch ({torch.__version__})")
        
        if torch.cuda.is_available():
            gpu_count = torch.cuda.device_count()
            gpu_name = torch.cuda.get_device_name(0) if gpu_count > 0 else "Unknown"
            print(f"✅ CUDA זמין - {gpu_count} GPUs ({gpu_name})")
            return True
        else:
            print("⚠️  CUDA לא זמין - יעבוד על CPU (יותר איטי)")
            return True
    except ImportError:
        print("❌ PyTorch לא מותקן")
        return False
    except Exception as e:
        print(f"❌ בעיה ב-PyTorch: {e}")
        return False

def check_demucs():
    """בדיקת Demucs"""
    try:
        from demucs.api import Separator
        print("✅ Demucs API זמין")
        
        # ניסיון ליצור separator (ללא הורדת מודל)
        try:
            separator = Separator(model="htdemucs", device="cpu")
            print("✅ Demucs htdemucs model נגיש")
            return True
        except Exception as e:
            print(f"⚠️  Demucs מותקן אבל יש בעיה במודל: {e}")
            print("   המודל יורד אוטומטית בהרצה הראשונה")
            return True
    except ImportError:
        print("❌ Demucs לא מותקן")
        return False
    except Exception as e:
        print(f"❌ בעיה ב-Demucs: {e}")
        return False

def main():
    print("🎵 musicRay - בדיקת תקינות המערכת\n")
    
    checks = [
        ("Python Version", check_python_version),
        ("FastAPI", lambda: check_package("fastapi")),
        ("Uvicorn", lambda: check_package("uvicorn")),
        ("PyTorch", check_torch_cuda),
        ("Demucs", check_demucs),
        ("Librosa", lambda: check_package("librosa")),
        ("SoundFile", lambda: check_package("soundfile")),
        ("NumPy", lambda: check_package("numpy")),
        ("SciPy", lambda: check_package("scipy")),
        ("FFmpeg", check_ffmpeg),
    ]
    
    results = []
    print("בודק רכיבי המערכת...\n")
    
    for name, check_func in checks:
        print(f"בודק {name}:")
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ שגיאה לא צפויה ב-{name}: {e}")
            results.append((name, False))
        print()
    
    # סיכום
    print("=" * 50)
    print("סיכום:")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {name}")
    
    print(f"\n{passed}/{total} בדיקות עברו בהצלחה")
    
    if passed == total:
        print("\n🎉 המערכת מוכנה לשימוש!")
        print("הרץ: python app.py או run.bat")
    elif passed >= total - 2:
        print("\n⚠️  המערכת כמעט מוכנה - יש בעיות קטנות")
        print("המערכת עשויה לעבוד אבל עם ביצועים מופחתים")
    else:
        print("\n❌ המערכת לא מוכנה - יש בעיות משמעותיות")
        print("אנא תקן את הבעיות לפני המשך")
    
    return passed == total

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nבדיקה בוטלה על ידי המשתמש")
    except Exception as e:
        print(f"\nשגיאה כללית: {e}")
    
    input("\nלחץ Enter לסגירה...")
