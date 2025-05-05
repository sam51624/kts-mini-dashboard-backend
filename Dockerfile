# 📌 1. ใช้ Python base image
FROM python:3.10-slim AS base

# 📌 2. ปิด interactive prompt
ENV PYTHONUNBUFFERED=1

# 📌 3. ติดตั้ง system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    python3-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 📌 4. กำหนด working directory
WORKDIR /app

# 📌 5. คัดลอก requirements.txt ก่อน (ช่วยใช้ cache)
COPY requirements.txt .

# 📌 6. ติดตั้ง Python packages
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 📌 7. คัดลอกโค้ดทั้งหมด
COPY . .

# 📌 8. กำหนด ENV สำหรับ Gunicorn และ Google Credentials
ENV PORT=8080
ENV GOOGLE_APPLICATION_CREDENTIALS="/etc/secrets/credentials.json"

# 📌 9. สั่ง Gunicorn รันแอป Flask (เช่น app.py)
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8080", "--workers=1", "--threads=8", "--timeout=0"]


