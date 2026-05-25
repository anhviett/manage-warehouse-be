FROM python:3.11-slim

# Ngăn Python tạo các file .pyc và delay log
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Cài đặt công cụ build, cài đặt pip packages, sau đó xóa công cụ build để giảm dung lượng image
COPY requirements.txt /app/

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    python3-dev \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get purge -y --auto-remove gcc python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY . /app/

EXPOSE 8000

# Chạy Django development server để hỗ trợ auto-reload khi code thay đổi
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
