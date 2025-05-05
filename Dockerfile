# 1. ใช้ Python image base
FROM python:3.10-slim AS base

# 2. ปิด interactive prompt ของ Python
ENV PYTHONUNBUFFERED=1

# 3. ติดตั้ง system dependencies ที่จำเป็น
RUN apt-get update && apt-get install -y \
    build-essential libffi-dev python3-dev curl \
    && rm -rf /var/lib/apt/lists/*

# 4. สร้าง working directory
WORKDIR /app

# 5. คัดลอก requirements.txt ก่อน เพื่อใช้ layer cache ได้
COPY requirements.txt .

# 6. ติดตั้ง Python packages
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# 7. คัดลอกไฟล์โปรเจกต์ทั้งหมด
COPY . .

# 8. ตั้งค่า ENV และรัน gunicorn
ENV PORT=8080
ENV GOOGLE_APPLICATION_CREDENTIALS="/etc/secrets/credentials.json"

# 9. รัน Flask app ด้วย Gunicorn
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8080", "--workers=1", "--threads=8", "--timeout=0"]

