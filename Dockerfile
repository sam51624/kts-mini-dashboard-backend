# 🔹 1. ใช้ Python image base
FROM python:3.10-slim

# 🔹 2. ปิด prompt interactive ของ Python
ENV PYTHONUNBUFFERED=1

# 🔹 3. ติดตั้ง system dependencies ที่จำเป็น
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    python3-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 🔹 4. Set working dir
WORKDIR /app

# 🔹 5. Copy project files ทั้งหมด
COPY . .

# 🔹 6. ติดตั้ง Python packages
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# 🔹 7. ให้ container รับ PORT จาก env
ENV PORT=8080

# 🔹 8. Path ไปยัง Service Account key (ถ้าใช้ Google Vision / Sheets API)
ENV GOOGLE_APPLICATION_CREDENTIALS="/etc/secrets/credentials.json"

# 🔹 9. ใช้ gunicorn รัน Flask app โดยรับ $PORT
CMD exec gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 0


