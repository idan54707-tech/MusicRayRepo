# 🐳 הוראות בניית Docker Image עבור musicRay Serverless

## 🎯 מטרה
בניית Docker Image עבור RunPod Serverless עם הBuilder הקיים שלך בענן.

---

## ⚙️ הגדרות שלך
- **DockerHub Repository**: `lennsura/repo`
- **Builder Name**: `builder-m`
- **Target Image**: `lennsura/repo:musicray-serverless`

---

## 🔧 שלב 1: הפעלת Docker Desktop

1. **הפעל Docker Desktop** (אם לא פועל):
   - לחץ על סמל Docker בשורת המשימות
   - או חפש "Docker Desktop" בתפריט התחל

2. **וודא ש-Docker פועל**:
   ```powershell
   docker --version
   ```

---

## 🏗️ שלב 2: בניית Image בענן

### אופציה A: עם הסקריפט (מומלץ)
```powershell
cd "C:\visual studio projects\musicRay\backend"
.\build-serverless.bat
```

### אופציה B: פקודה ישירה
```powershell
cd "C:\visual studio projects\musicRay\backend"

docker buildx build \
  --builder builder-m \
  --platform linux/amd64 \
  --file Dockerfile.serverless \
  --tag lennsura/repo:musicray-serverless \
  --tag lennsura/repo:latest \
  --push \
  .
```

---

## 🎯 שלב 3: אימות הבנייה

אחרי הבנייה, וודא שה-Image הועלה:

```powershell
docker buildx imagetools inspect lennsura/repo:musicray-serverless
```

---

## 🏃 שלב 4: יצירת RunPod Serverless Endpoint

1. **כנס ל-[RunPod.io](https://runpod.io)**
2. **עבור ל-Serverless** בתפריט
3. **לחץ על "New Endpoint"**
4. **מלא פרטים**:
   - **Name**: `musicray-separator`
   - **Docker Image**: `lennsura/repo:musicray-serverless`
   - **Container Registry**: Docker Hub (public)

5. **הגדרות GPU מומלצות**:
   ```json
   {
     "containerDiskInGb": 20,
     "gpuIds": "AMPERE_24",
     "idleTimeout": 5,
     "locations": {
       "EU-RO-1": {
         "gpuIds": "AMPERE_24",
         "workersMin": 0,
         "workersMax": 3
       }
     }
   }
   ```

6. **שמור API Key ו-Endpoint ID** שתקבל!

---

## 🧪 שלב 5: בדיקת Endpoint

```bash
curl -X POST "https://api.runpod.ai/v2/YOUR-ENDPOINT-ID/runsync" \
  -H "Authorization: Bearer YOUR-API-KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "file_url": "https://example.com/test-song.mp3"
    }
  }'
```

---

## 🎉 שלב 6: אינטגרציה עם Frontend

1. **הפעל את הFrontend**: `npm run dev`
2. **הפעל את ה-toggle "RunPod Serverless"**
3. **הכנס API Key ו-Endpoint ID**
4. **העלה שיר ותהנה!** 🎵

---

## 🔍 פתרון בעיות

### Docker לא מזוהה:
```powershell
# אתחל PowerShell או הוסף ל-PATH:
$env:PATH += ";C:\Program Files\Docker\Docker\resources\bin"
```

### Builder לא קיים:
```powershell
# צור builder חדש:
docker buildx create --name builder-m --use
```

### שגיאות בנייה:
- וודא שאתה מחובר ל-DockerHub: `docker login`
- בדוק שהBuilder פועל: `docker buildx ls`

---

## 💰 עלויות צפויות

| GPU Type | עלות/שעה | עלות לשיר (4 דק') |
|----------|-----------|-------------------|
| RTX A4000 | $0.79 | ~$0.05 |
| RTX A5000 | $1.14 | ~$0.08 |
| RTX 4090 | $0.83 | ~$0.06 |

**חיסכון של ~70% מPod רגיל!** 🎯

---

## ✅ Checklist

- [ ] Docker Desktop מותקן ופועל
- [ ] מחובר ל-DockerHub (`docker login`)
- [ ] Builder `builder-m` זמין
- [ ] Image נבנה ונדחף לריפו
- [ ] RunPod Endpoint נוצר
- [ ] API Key ו-Endpoint ID נשמרו
- [ ] Frontend מוגדר עם הפרטים
- [ ] בדיקה ראשונה עברה בהצלחה

**🚀 מוכן לעיבוד מקצועי בענן!**
