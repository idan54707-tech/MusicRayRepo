# 🏃 musicRay - פריסה ל-RunPod Serverless

## מדריך מלא לפריסת musicRay על RunPod Serverless

### 🎯 יתרונות Serverless:
- **💰 חיסכון בעלויות** - שלם רק על זמן עיבוד בפועל
- **⚡ מהירות** - אוטו-scaling מהיר
- **🔧 ללא תחזוקה** - אין צורך לנהל שרתים
- **📈 גמישות** - מתאים לעומסים משתנים

---

## 📋 שלב 1: הכנת Docker Image

### בניית Image מקומית (לבדיקה):
```bash
cd backend
docker build -f Dockerfile.serverless -t musicray-serverless .
```

### בדיקת Image:
```bash
# בדיקה מהירה
docker run --rm musicray-serverless python -c "import torch; import demucs; print('✅ OK')"

# בדיקת Handler (אם יש קובץ דוגמה)
python test_handler.py
```

---

## 🐳 שלב 2: העלאה ל-Docker Hub

```bash
# תיוג Image
docker tag musicray-serverless YOUR-USERNAME/musicray-serverless:latest

# העלאה
docker push YOUR-USERNAME/musicray-serverless:latest
```

---

## 🏃 שלב 3: יצירת Serverless Endpoint ב-RunPod

### 3.1 כניסה ל-RunPod Console
1. היכנס ל-[RunPod.io](https://runpod.io)
2. עבור ל-**Serverless** בתפריט

### 3.2 יצירת Endpoint חדש
1. לחץ **+ New Endpoint**
2. מלא פרטים:
   - **Name**: `musicray-separator`
   - **Docker Image**: `YOUR-USERNAME/musicray-serverless:latest`
   - **Container Registry Credentials**: אם נדרש

### 3.3 הגדרות מתקדמות:
```json
{
  "containerDiskInGb": 20,
  "gpuIds": "AMPERE_24",
  "name": "musicray-separator",
  "env": {},
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

### 3.4 פרמטרים מומלצים:
- **GPU**: RTX A4000/A5000 (24GB VRAM)
- **Idle Timeout**: 5 שניות (חיסכון בעלויות)
- **Max Workers**: 3 (למקרה של עומס)
- **Container Disk**: 20GB (למודלי Demucs)

---

## 📡 שלב 4: שימוש ב-API

### 4.1 קבלת API Key ו-Endpoint URL
אחרי יצירת ה-Endpoint תקבל:
- **Endpoint ID**: `your-endpoint-id`
- **API Key**: שמור בסוד!

### 4.2 קריאה ל-API:

#### Python Example:
```python
import requests
import json

# הגדרות
RUNPOD_API_KEY = "your-api-key"
ENDPOINT_ID = "your-endpoint-id"
RUNPOD_URL = f"https://api.runpod.ai/v2/{ENDPOINT_ID}/runsync"

# נתוני הקלט
payload = {
    "input": {
        "file_url": "https://example.com/song.mp3"
    }
}

# שליחת הבקשה
headers = {
    "Authorization": f"Bearer {RUNPOD_API_KEY}",
    "Content-Type": "application/json"
}

response = requests.post(RUNPOD_URL, json=payload, headers=headers, timeout=600)

if response.status_code == 200:
    result = response.json()
    print("✅ עיבוד הושלם!")
    print(json.dumps(result, indent=2))
else:
    print(f"❌ שגיאה: {response.status_code} - {response.text}")
```

#### cURL Example:
```bash
curl -X POST "https://api.runpod.ai/v2/YOUR-ENDPOINT-ID/runsync" \
  -H "Authorization: Bearer YOUR-API-KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "file_url": "https://example.com/song.mp3"
    }
  }'
```

---

## 🔄 שלב 5: אינטגרציה עם Frontend

עדכן את `frontend/lib/api.ts`:

```typescript
// הוסף תמיכה ב-RunPod Serverless
export class RunPodServerlessClient {
  private apiKey: string;
  private endpointId: string;

  constructor(apiKey: string, endpointId: string) {
    this.apiKey = apiKey;
    this.endpointId = endpointId;
  }

  async separateAudio(fileUrl: string): Promise<any> {
    const url = `https://api.runpod.ai/v2/${this.endpointId}/runsync`;
    
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        input: { file_url: fileUrl }
      })
    });

    if (!response.ok) {
      throw new Error(`RunPod API error: ${response.statusText}`);
    }

    return await response.json();
  }
}
```

---

## 📊 שלב 6: ניטור ועלויות

### 6.1 ניטור בזמן אמת:
- **RunPod Console** → **Serverless** → **Analytics**
- מעקב אחרי:
  - זמני תגובה
  - שגיאות
  - עלויות

### 6.2 אופטימיזציית עלויות:
```json
{
  "idleTimeout": 5,        // כיבוי מהיר אחרי סיום
  "workersMin": 0,         // ללא workers קבועים
  "workersMax": 2,         // הגבלת מקסימום
  "gpuIds": "AMPERE_16"    // GPU חזק אבל לא יקר מדי
}
```

---

## 🧪 שלב 7: בדיקות ו-Debug

### בדיקת Endpoint:
```bash
# בדיקת health
curl -X POST "https://api.runpod.ai/v2/YOUR-ENDPOINT-ID/runsync" \
  -H "Authorization: Bearer YOUR-API-KEY" \
  -H "Content-Type: application/json" \
  -d '{"input": {"file_url": "https://www.soundjay.com/misc/sounds/bell-ringing-05.wav"}}'
```

### לוגים ו-Debug:
- **RunPod Console** → **Serverless** → **Logs**
- שימוש ב-`print()` statements ב-Handler
- בדיקת timeout settings

---

## 💡 טיפים מתקדמים

### 1. **Pre-warming**:
```python
# הוסף ל-Handler כדי לחמם את המודל
SEPARATOR = None

def get_separator():
    global SEPARATOR
    if SEPARATOR is None:
        from demucs.api import Separator
        SEPARATOR = Separator(model='htdemucs', device=DEVICE)
    return SEPARATOR
```

### 2. **Error Handling**:
```python
def handler(event):
    try:
        # ... קוד עיקרי
        return {"success": True, "data": result}
    except Exception as e:
        return {
            "success": False, 
            "error": str(e),
            "error_type": type(e).__name__
        }
```

### 3. **Performance Monitoring**:
```python
import time

def handler(event):
    start_time = time.time()
    # ... עיבוד
    processing_time = time.time() - start_time
    
    return {
        "success": True,
        "processing_time_seconds": processing_time,
        "data": result
    }
```

---

## 📈 השוואת עלויות

| סוג | עלות/שעה | עלות לשיר (4 דק') | מתי להשתמש |
|-----|-----------|-------------------|-------------|
| **Pod קבוע** | $0.50-0.80 | $0.03-0.05 | עומס קבוע |
| **Serverless** | $0.80-1.20 | $0.05-0.08 | עומס משתנה |
| **Spot Instance** | $0.20-0.40 | $0.01-0.03 | לא דחוף |

**מסקנה**: Serverless מושלם לשימוש לא רציף! 💰

---

## ✅ Checklist לפריסה

- [ ] Docker Image נבנה ונבדק מקומית
- [ ] Image הועלה ל-Docker Hub
- [ ] Endpoint נוצר ב-RunPod
- [ ] API Key נשמר בבטחה
- [ ] בדיקה עם קובץ דוגמה
- [ ] אינטגרציה עם Frontend
- [ ] הגדרת ניטור ואלרטים

**🚀 מוכן לעיבוד מקצועי בענן!**
