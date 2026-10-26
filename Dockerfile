FROM python:3.12-slim

# tzdata de ZoneInfo("Asia/Ho_Chi_Minh") hoat dong
RUN apt-get update \
    && apt-get install -y --no-install-recommends tzdata \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TZ=Asia/Ho_Chi_Minh

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY sql/ ./sql/
COPY app/ ./app/

# Chay bang user thuong, khong phai root
RUN useradd --create-home --shell /usr/sbin/nologin dmb \
    && chown -R dmb:dmb /app
USER dmb

CMD ["python", "-m", "app.monitor"]
