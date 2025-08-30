@echo off
REM Build script for musicRay Serverless on DockerHub (Windows)

echo 🚀 Building musicRay Serverless for RunPod...
echo 📦 Repository: lennsura/repo
echo 🏗️ Builder: builder-m

REM Build and push to DockerHub using cloud builder
docker buildx build ^
  --builder builder-m ^
  --platform linux/amd64 ^
  --file Dockerfile.serverless ^
  --tag lennsura/repo:musicray-serverless ^
  --tag lennsura/repo:latest ^
  --push ^
  .

echo ✅ Build completed!
echo 🎯 Image: lennsura/repo:musicray-serverless
echo 🏃 Ready for RunPod Serverless deployment!
