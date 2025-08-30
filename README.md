# 🎵 musicRay - פירוק שירים לסטמים

**musicRay** הוא MVP של ווב-אפליקציה שמפרקת שירים ל-4 סטמים (Vocals/Drums/Bass/Other) ומציגה מיקסר אינטראקטיבי ויזואלי עם waveforms, פיידרים ובקרות מתקדמות.

## ✨ תכונות עיקריות

- **הפרדת סטמים מתקדמת** - באמצעות Demucs v4 עם פרמטרים איכותיים
- **מיקסר ויזואלי אינטראקטיבי** - פיידרים, Mute/Solo, waveforms
- **סנכרון מושלם** - Web Audio API עם drift guard ו-latency compensation
- **Post-Processing** - נורמליזציה, סינון תדרים, הפחתת רעשים
- **ניתוח מוזיקלי** - זיהוי BPM ומפתח מוזיקלי אוטומטי
- **לולאות אינטראקטיביות** - יצירת A-B loops על ידי גרירה
- **UI מודרני ויפה** - עיצוב כמו BandLab עם TailwindCSS

## 🏗️ ארכיטקטורה

### Backend
- **Python + FastAPI** - API מהיר ויעיל
- **Demucs v4** - מודל AI מתקדם להפרדת סטמים
- **PyTorch + CUDA** - עיבוד GPU מהיר
- **librosa** - ניתוח שמע ו-BPM/Key detection
- **Post-processing pipeline** - שיפור איכות אוטומטי

### Frontend
- **Next.js + TypeScript** - React מתקדם עם type safety
- **Web Audio API** - ניגון מסונכרן ובקרה מדויקת
- **Wavesurfer.js** - waveforms אינטראקטיביים
- **TailwindCSS** - עיצוב מודרני ורספונסיבי

### Infrastructure
- **Docker + CUDA** - deployment קל על GPU
- **Local storage** - קבצים זמניים עם ניקוי אוטומטי
- **CORS enabled** - תמיכה מלאה ב-development

## 🚀 התקנה והרצה

### דרישות מערכת
- **Python 3.8+**
- **Node.js 18+**
- **CUDA 12.1** (אופציונלי, לביצועים מהירים)
- **ffmpeg**

### הרצה מקומית (Development)

#### אופציה 1: התקנה אוטומטית (Windows)
```bash
cd backend

# התקנה אוטומטית
install.bat

# הרצת השרת
run.bat
```

#### אופציה 2: התקנה ידנית
```bash
cd backend

# יצירת virtual environment
python -m venv venv

# הפעלת virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# התקנת תלויות (CPU)
pip install -r requirements-cpu.txt

# או עבור GPU:
pip install -r requirements-gpu.txt

# בדיקת תקינות המערכת
python test_setup.py

# הרצת השרת
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

#### 2. Frontend Setup
```bash
cd frontend

# התקנת תלויות
npm install

# הרצת dev server
npm run dev
```

השרת יהיה זמין ב: http://localhost:3000

### הרצה עם Docker (Production)

#### Backend על GPU
```bash
cd backend
docker build -t musicray-backend .
docker run --gpus all -p 8000:8000 musicray-backend
```

#### Frontend
```bash
cd frontend
npm run build
npm start
```

### הרצה בענן (RunPod מומלץ)

#### 🏃 RunPod - הכי נוח ומהיר

**אופציה 1: סקריפט אוטומטי (מומלץ)**
```bash
# ב-RunPod Pod:
curl -sSL https://raw.githubusercontent.com/YOUR-USERNAME/musicRay/main/runpod-quick-setup.sh | bash
```

**אופציה 2: התקנה ידנית**
```bash
# 1. צור Pod חדש ב-runpod.io
# 2. בחר GPU: RTX 4090/3090 מומלץ
# 3. Image: runpod/pytorch:2.1.0-py3.10-cuda12.1.1-devel-ubuntu22.04

# התקנה מהירה
cd /workspace
git clone <your-repo-url>
cd musicRay/backend
pip install -r requirements-gpu.txt
python test_setup.py  # בדיקת תקינות
uvicorn app:app --host 0.0.0.0 --port 8000

# ה-API יהיה זמין ב:
# https://your-pod-id-8000.proxy.runpod.net
```

**🎯 חיבור ב-Frontend:**
1. הפעל את ה-toggle "עיבוד בענן"
2. הכנס את ה-URL: `https://your-pod-id-8000.proxy.runpod.net`
3. לחץ "בדוק" לוודא שהחיבור עובד
4. העלה שיר - יעובד בענן! 🚀

#### ביצועים ועלויות
- **RTX 4090**: ~2-3 דקות לשיר | ~$0.80/שעה
- **RTX 3090**: ~3-4 דקות לשיר | ~$0.50/שעה  
- **RTX 3080**: ~4-6 דקות לשיר | ~$0.40/שעה

📖 **מדריך מפורט**: ראה `runpod-setup.md`

## 📖 שימוש

### העלאת שיר
1. גרור קובץ שמע או לחץ לבחירה
2. תומך ב: MP3, WAV, FLAC, M4A
3. הגבלות: עד 100MB, עד 10 דקות
4. המתן לעיבוד (1-5 דקות לפי אורך השיר)

### מיקסר
- **Play/Pause** - השמעה ועצירה
- **Stop** - עצירה מלאה וחזרה להתחלה
- **Loop** - לולאה אינסופית
- **Volume Faders** - בקרת ווליום לכל סטם
- **Mute (M)** - השתקת סטם
- **Solo (S)** - השמעת סטם בודד
- **Waveform** - לחיצה לקפיצה, גרירה ללולאה

### תכונות מתקדמות
- **Sync Guard** - בדיקה כל 5 שניות ותיקון drift
- **Smooth Transitions** - אין clicks/pops בשינוי ווליום
- **Latency Compensation** - סנכרון מושלם בין סטמים
- **Auto Cleanup** - מחיקת קבצים זמניים

## 🔧 API Endpoints

### POST /upload
העלאת קובץ שמע לעיבוד
- **Input**: FormData עם קובץ
- **Output**: JSON עם URLs של סטמים + metadata

### GET /files/{job_id}/{stem}.wav  
הורדת קובץ סטם
- **Parameters**: job_id, stem name
- **Output**: קובץ WAV

### DELETE /files/{job_id}
מחיקת כל קבצי ה-job
- **Parameters**: job_id
- **Output**: הודעת אישור

### GET /health
בדיקת תקינות השרת
- **Output**: מצב השרת

## 🎛️ הגדרות מתקדמות

### Demucs Parameters
```python
--shifts 2          # הפחתת artifacts
--overlap 0.25      # חפיפה טובה יותר  
--segment 6         # פלחים קטנים לדיוק
```

### Post-Processing
- **LUFS Normalization** - -14 LUFS לכל הסטמים
- **Frequency Filtering** - HPF/LPF לפי סוג הסטם
- **Phase Alignment** - תיקון פאזה בין ערוצים
- **Fade In/Out** - מניעת clicks

### Audio Engine Settings
```typescript
latencyCompensation: 100ms    // פיצוי עיכוב
syncCheckInterval: 5000ms     // בדיקת סנכרון
rampTime: 20ms               // זמן שינוי gain
```

## 🛠️ פיתוח והרחבות

### מבנה הפרויקט
```
musicRay/
├── backend/
│   ├── app.py              # FastAPI main
│   ├── separate.py         # הפרדת סטמים
│   ├── postprocess.py      # עיבוד מתקדם
│   ├── analysis.py         # BPM/Key detection
│   └── requirements.txt    # תלויות Python
├── frontend/
│   ├── pages/              # Next.js pages
│   ├── components/         # React components
│   ├── lib/               # API client & Audio Engine
│   └── styles/            # TailwindCSS
└── storage/               # קבצים זמניים
```

### הוספת תכונות חדשות

#### Backend
1. הוסף endpoint חדש ב-`app.py`
2. צור פונקציה ב-module מתאים
3. עדכן requirements אם נדרש

#### Frontend  
1. הוסף component ב-`components/`
2. עדכן `AudioEngine` לתכונות שמע
3. עדכן API client ב-`lib/api.ts`

### TODO List להרחבות עתידיות
- [ ] **UVR-MDX-Net integration** - מודל נוסף לווקלס
- [ ] **Chord detection** - זיהוי אקורדים עם timeline
- [ ] **AI Chat** - "שאל את ה-AI" על השיר
- [ ] **User accounts** - שמירת פרויקטים
- [ ] **Batch processing** - תור עיבוד
- [ ] **More instruments** - גיטרה, פסנתר, וכו'
- [ ] **Real-time effects** - reverb, EQ, compressor
- [ ] **Export options** - MP3, stems package

## 🐛 בעיות נפוצות ופתרונות

### Backend לא מתחיל

#### שגיאת PyTorch/CUDA
```bash
# אם יש שגיאה עם torch==2.2.2+cu121:
cd backend
pip install -r requirements-cpu.txt  # עבור CPU בלבד

# או עבור GPU:
pip install -r requirements-gpu.txt
```

#### uvicorn לא מוכר
```bash
# וודא שה-virtual environment פעיל:
# Windows:
venv\Scripts\activate
# Linux/Mac: 
source venv/bin/activate

# ואז:
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

#### בדיקת מערכת כללית
```bash
# הרץ בדיקת תקינות:
cd backend
python test_setup.py

# בדוק שPython 3.8+ מותקן
python --version

# התקן ffmpeg
# Ubuntu: sudo apt install ffmpeg  
# macOS: brew install ffmpeg
# Windows: https://ffmpeg.org/download.html

# בדוק CUDA (אופציונלי)
python -c "import torch; print(torch.cuda.is_available())"
```

### Frontend לא טוען
```bash
# בדוק Node.js version
node --version  # צריך 18+

# נקה cache
rm -rf .next node_modules
npm install
```

### שגיאות CORS
- וודא שה-Backend רץ על port 8000
- בדוק שה-CORS middleware מוגדר נכון
- בפרודקשן עדכן את `allow_origins`

### איכות הפרדה לא טובה
- השתמש בקבצים באיכות גבוהה (44.1kHz+)
- נסה שירים עם הפרדה ברורה בין כלים
- שקול שימוש ב-GPU לביצועים טובים יותר

### בעיות סנכרון
- בדוק שהדפדפן תומך ב-Web Audio API
- נסה להפחית latency compensation
- וודא שאין טאבים אחרים שמשתמשים בשמע

## 📄 רישיון ומדיניות

**הכלי מיועד ללמידה וניתוח אישי בלבד.**

- ✅ ניתן לשתף את הקוד (MIT License)
- ✅ ניתן למחוק חומרים בכל עת
- ❌ אין לשתף חומרים מוגני זכויות ללא רשות
- ❌ אין להשתמש למטרות מסחריות ללא אישור

## 🤝 תרומה

רוצה לתרום לפרויקט? מעולה!

1. **Fork** את הפרויקט
2. **צור branch** לתכונה שלך
3. **Commit** את השינויים
4. **Push** ל-branch
5. **פתח Pull Request**

אנו מחפשים תרומות ב:
- שיפור אלגוריתמי הפרדה
- תכונות UI/UX חדשות  
- אופטימיזציות ביצועים
- תיקון באגים
- תיעוד ובדיקות

## 📞 צור קשר ותמיכה

- **Issues**: פתח issue ב-GitHub
- **Discussions**: דיונים קהילתיים
- **Email**: support@musicray.dev (לעתיד)

---

**נבנה עם ❤️ ו-🎵 על ידי צוות musicRay**

*מוכן להפוך כל שיר לחוויה אינטראקטיבית!*
#   M u s i c R a y  
 