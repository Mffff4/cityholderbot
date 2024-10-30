FROM python:3.11-slim-bullseye

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    xvfb \
    libxi6 \
    libgconf-2-4 \
    gcc \
    python3-dev \
    default-jdk \
    chromium \
    chromium-driver \
    xauth \
    xorg \
    dbus-x11 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p sessions webdriver \
    && chmod -R 777 /app

ENV PYTHONUNBUFFERED=1 \
    CHROME_BIN=/usr/bin/chromium \
    CHROMEDRIVER_PATH=/usr/bin/chromedriver \
    DISPLAY=:99 \
    DBUS_SESSION_BUS_ADDRESS=/dev/null

CMD ["python", "main.py", "-a", "2"]
