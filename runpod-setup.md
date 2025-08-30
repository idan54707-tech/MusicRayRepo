# 🏃 הגדרת musicRay על RunPod

## מדריך מהיר לפריסה על RunPod

### 1. יצירת Pod

1. היכנס ל-[RunPod.io](https://runpod.io)
2. לחץ על "Deploy" → "GPU Pod"
3. בחר GPU חזק:
   - **מומלץ**: RTX 4090 (24GB VRAM) - מהיר ביותר
   - **אלטרנטיבה**: RTX 3090 (24GB VRAM) - טוב וזול יותר
   - **מינימום**: RTX 3080 (10GB VRAM) - עובד אבל יותר איטי

### 2. הגדרת Container

```bash
# Image: runpod/pytorch:2.1.0-py3.10-cuda12.1.1-devel-ubuntu22.04
# Container Disk: 20GB (מינימום)
# Volume: לא נדרש למטרות פיתוח
```

### 3. פריסת הקוד

#### אופציה א': העלאה ישירה
```bash
# התחבר ל-Pod דרך SSH או Web Terminal
cd /workspace

# שכפול הפרויקט
git clone https://github.com/your-username/musicRay.git
cd musicRay/backend

# התקנת תלויות
pip install -r requirements-gpu.txt

# בדיקת תקינות
python test_setup.py

# הרצה
uvicorn app:app --host 0.0.0.0 --port 8000
```

#### אופציה ב': Docker Build
```bash
cd /workspace
git clone https://github.com/your-username/musicRay.git
cd musicRay

# בניית Docker image
docker build -f backend/Dockerfile.runpod -t musicray-runpod backend/

# הרצה
docker run --gpus all -p 8000:8000 -e RUNPOD_POD_ID=$RUNPOD_POD_ID musicray-runpod
```

### 4. חיבור Frontend

#### אופציה א': Frontend מקומי
```bash
# במחשב המקומי
cd frontend
npm install

# עדכן את ה-API URL ב-.env.local
echo "NEXT_PUBLIC_API_URL=https://your-pod-id-8000.proxy.runpod.net" > .env.local

# הרץ
npm run dev
```

#### אופציה ב': Frontend גם על RunPod
```bash
# ב-Pod
cd /workspace/musicRay/frontend
npm install
npm run build

# הגדר proxy ל-port 3000
npm start
```

### 5. URLs וגישה

```bash
# Backend API
https://your-pod-id-8000.proxy.runpod.net

# Frontend (אם רץ על RunPod)  
https://your-pod-id-3000.proxy.runpod.net

# SSH Access
ssh root@your-pod-id.proxy.runpod.net -p 22
```

## ⚡ אופטימיזציות לRunPod

### זיכרון GPU
```python
# הגדרות מותאמות ב-separate.py
if IS_RUNPOD:
    # פרמטרים לניצול מקסימלי של GPU
    --shifts 10      # איכות מקסימלית
    --segment 16     # פלחים גדולים
    --overlap 0.5    # חפיפה מקסימלית
```

### ביצועים
- **RTX 4090**: ~2-3 דקות לשיר של 4 דקות
- **RTX 3090**: ~3-4 דקות לשיר של 4 דקות  
- **RTX 3080**: ~4-6 דקות לשיר של 4 דקות

### עלויות (לשעה)
- **RTX 4090**: ~$0.80/hour
- **RTX 3090**: ~$0.50/hour
- **RTX 3080**: ~$0.40/hour

## 🔧 בדיקת תקינות

```bash
# בדיקת GPU
nvidia-smi

# בדיקת PyTorch + CUDA
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}, GPU: {torch.cuda.get_device_name()}')"

# בדיקת Demucs
python -c "from demucs.api import Separator; print('Demucs OK')"

# בדיקת API
curl http://localhost:8000/health
```

## 📊 ניטור ביצועים

```bash
# ניטור GPU בזמן אמת
watch -n 1 nvidia-smi

# ניטור זיכרון
htop

# לוגים של האפליקציה
tail -f /app/logs/app.log
```

## 🛠️ טיפים מתקדמים

### 1. שמירת מודלים
```bash
# שמור מודלים ב-persistent storage
mkdir -p /workspace/models
export TORCH_HOME=/workspace/models
```

### 2. Batch Processing
```python
# עבד מספר שירים במקביל
# (זהיר מזיכרון GPU!)
async def process_multiple_songs(files):
    tasks = [separate_audio(f) for f in files[:3]]  # מקס 3 במקביל
    return await asyncio.gather(*tasks)
```

### 3. Auto-shutdown
```bash
# הגדר auto-shutdown לחסכון בעלויות
echo "shutdown -h +60" | at now  # כיבוי אחרי שעה
```

## 🚨 בעיות נפוצות

### Out of Memory
```bash
# הקטן segment size
--segment 4  # במקום 16

# או הקטן batch size
--shifts 2   # במקום 10
```

### Connection Timeout
```bash
# הגדל timeout ב-frontend
const API_TIMEOUT = 30 * 60 * 1000;  // 30 דקות
```

### Slow Performance
```bash
# בדוק שGPU בשימוש
nvidia-smi

# בדוק שלא רץ על CPU
export CUDA_VISIBLE_DEVICES=0
```

## 🎯 המלצות

1. **התחל עם RTX 3090** - יחס מחיר/ביצועים הטוב ביותר
2. **השתמש ב-Spot Instances** - עד 50% חיסכון
3. **שמור מודלים** - הורדה חד-פעמית של 2GB
4. **נטר עלויות** - הגדר alerts ב-RunPod
5. **בדוק logs** - לאבחון בעיות מהר

---

**מוכן לעיבוד מקצועי של שירים עם GPU! 🚀**
