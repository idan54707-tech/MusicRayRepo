# Dockerfile עבור musicRay Backend עם תמיכה ב-GPU
FROM nvidia/cuda:12.1.0-cudnn8-runtime-ubuntu22.04

# הגדרת משתני סביבה
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# התקנת חבילות מערכת
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-dev \
    ffmpeg \
    git \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# יצירת תיקיית עבודה
WORKDIR /app

# העתקת requirements ראשון לאופטימיזציה של cache
COPY requirements.txt .

# התקנת תלויות Python
RUN pip3 install --upgrade pip setuptools wheel
RUN pip3 install -r requirements.txt

# העתקת קוד האפליקציה
COPY . .

# יצירת תיקיית storage
RUN mkdir -p storage

# הרצת הדאונלוד הראשוני של מודלי Demucs (אופציונלי)
RUN python3 -c "import torch; print('PyTorch version:', torch.__version__); print('CUDA available:', torch.cuda.is_available())"

# פתיחת פורט
EXPOSE 8000

# הגדרת health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# הרצת האפליקציה
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
