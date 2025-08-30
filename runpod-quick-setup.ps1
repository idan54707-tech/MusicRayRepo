# 🏃 musicRay - RunPod Quick Setup Script (PowerShell)
# הרץ את הסקריפט הזה ב-RunPod Pod (Windows container) כדי להגדיר את musicRay

Write-Host "🎵 musicRay RunPod Quick Setup" -ForegroundColor Cyan
Write-Host "==============================" -ForegroundColor Cyan

# בדיקת סביבה
Write-Host "📍 בודק סביבת RunPod..." -ForegroundColor Yellow
$podId = $env:RUNPOD_POD_ID
if ($podId) {
    Write-Host "✅ RunPod Pod ID: $podId" -ForegroundColor Green
} else {
    Write-Host "⚠️  לא זוהה RunPod Pod ID, אבל ממשיך..." -ForegroundColor Yellow
}

# בדיקת GPU
Write-Host "🎮 בודק GPU..." -ForegroundColor Yellow
try {
    $gpuInfo = nvidia-smi --query-gpu=name,memory.total --format=csv,noheader,nounits
    Write-Host "✅ GPU: $gpuInfo" -ForegroundColor Green
} catch {
    Write-Host "❌ nvidia-smi לא נמצא" -ForegroundColor Red
}

# מעבר לתיקיית עבודה
Set-Location /workspace

# בדיקה אם הפרויקט כבר קיים
if (Test-Path "musicRay") {
    Write-Host "📁 musicRay כבר קיים, מעדכן..." -ForegroundColor Yellow
    Set-Location musicRay
    git pull
} else {
    Write-Host "📥 משכפל את musicRay..." -ForegroundColor Yellow
    # החלף את ה-URL הזה עם הכתובת של הרפו שלך
    git clone https://github.com/YOUR-USERNAME/musicRay.git
    Set-Location musicRay
}

# מעבר לbackend
Set-Location backend

Write-Host "🐍 מתקין תלויות Python..." -ForegroundColor Yellow
pip install --upgrade pip
pip install -r requirements-gpu.txt

Write-Host "🧪 בודק התקנה..." -ForegroundColor Yellow
python -c @"
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
"@

Write-Host "🚀 מתחיל שרת..." -ForegroundColor Green
Write-Host ""
Write-Host "📋 מידע חשוב:" -ForegroundColor Cyan
Write-Host "   Backend URL: https://$podId-8000.proxy.runpod.net" -ForegroundColor White
Write-Host "   Health Check: Invoke-WebRequest https://$podId-8000.proxy.runpod.net/health" -ForegroundColor White
Write-Host ""
Write-Host "🎯 העתק את ה-URL הזה למערכת musicRay שלך!" -ForegroundColor Yellow
Write-Host ""

# הרצת השרת
uvicorn app:app --host 0.0.0.0 --port 8000
