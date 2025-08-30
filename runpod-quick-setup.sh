#!/bin/bash

# 🏃 musicRay - RunPod Quick Setup Script
# הרץ את הסקריפט הזה ב-RunPod Pod כדי להגדיר את musicRay במהירות

set -e

echo "🎵 musicRay RunPod Quick Setup"
echo "=============================="

# בדיקת סביבה
echo "📍 בודק סביבת RunPod..."
if [ -n "$RUNPOD_POD_ID" ]; then
    echo "✅ RunPod Pod ID: $RUNPOD_POD_ID"
else
    echo "⚠️  לא זוהה RunPod Pod ID, אבל ממשיך..."
fi

# בדיקת GPU
echo "🎮 בודק GPU..."
if command -v nvidia-smi &> /dev/null; then
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader,nounits
else
    echo "❌ nvidia-smi לא נמצא"
fi

# עדכון מערכת
echo "📦 מעדכן חבילות מערכת..."
apt-get update -qq
apt-get install -y -qq git wget curl ffmpeg

# מעבר לתיקיית עבודה
cd /workspace

# בדיקה אם הפרויקט כבר קיים
if [ -d "musicRay" ]; then
    echo "📁 musicRay כבר קיים, מעדכן..."
    cd musicRay
    git pull
else
    echo "📥 משכפל את musicRay..."
    # החלף את ה-URL הזה עם הכתובת של הרפו שלך
    git clone https://github.com/YOUR-USERNAME/musicRay.git
    cd musicRay
fi

# מעבר לbackend
cd backend

echo "🐍 מתקין תלויות Python..."
pip install --upgrade pip
pip install -r requirements-gpu.txt

echo "🧪 בודק התקנה..."
python -c "
import torch
print(f'✅ PyTorch: {torch.__version__}')
print(f'✅ CUDA Available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'✅ GPU: {torch.cuda.get_device_name()}')
    print(f'✅ GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f}GB')

try:
    import demucs
    print('✅ Demucs imported successfully')
except Exception as e:
    print(f'❌ Demucs error: {e}')
"

echo "🚀 מתחיל שרת..."
echo ""
echo "📋 מידע חשוב:"
echo "   Backend URL: https://${RUNPOD_POD_ID:-YOUR-POD-ID}-8000.proxy.runpod.net"
echo "   Health Check: curl https://${RUNPOD_POD_ID:-YOUR-POD-ID}-8000.proxy.runpod.net/health"
echo ""
echo "🎯 העתק את ה-URL הזה למערכת musicRay שלך!"
echo ""

# הרצת השרת
uvicorn app:app --host 0.0.0.0 --port 8000
