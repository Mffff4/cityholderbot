# City Holder Bot 🏠

[![Bot Link](https://img.shields.io/badge/Telegram-Бот_Link-blue?style=for-the-badge&logo=Telegram&logoColor=white)](https://t.me/cityholder/game?startapp=228618799)
[![Channel Link](https://img.shields.io/badge/Telegram-Канал_Link-blue?style=for-the-badge&logo=Telegram&logoColor=white)](https://t.me/+0C-gh0mKBzxiNzky)
[![Channel Link](https://img.shields.io/badge/Сборник_ботов-Link-blue?style=for-the-badge&logo=Telegram&logoColor=white)](https://t.me/+uF4lQD9ZEUE4NGUy)
---

## 📑 Оглавление
1. [Описание](#описание)
2. [Ключевые особенности](#ключевые-особенности)
3. [Установка](#установка)
   - [Быстрый старт](#быстрый-старт)
   - [Ручная установка](#ручная-установка)
   - [Установка с помощью Docker (рекомендуемый вариант)](#установка-с-помощью-docker)
4. [Настройки](#настройки)
5. [Поддержка и донаты](#поддержка-и-донаты)
6. [Контакты](#контакты)
7. [Дисклеймер](#дисклеймер)
---

## 📜 Описание
City Holder Bot — это автоматизированный бот для игры City Holder в Telegram. Он помогает управлять городом, собирать ресурсы и выполнять улучшения автоматически.

## 🌟 Ключевые особенности
- 🏙️ Автоматическое управление городом
- 💰 Сбор ресурсов и выполнение тапов
- 🏗️ Автоматические улучшения зданий
- 🔄 Поддержка нескольких аккаунтов
- 🌐 Работа через прокси
---

## 🛠️ Установка

### Быстрый старт
1. **Скачайте проект:**
   ```bash
   git clone https://github.com/Mffff4/cityholderbot.git
   cd cityholder
   ```

2. **Установите зависимости:**
   - **Windows**:
     ```bash
     run.bat
     ```
   - **Linux**:
     ```bash
     run.sh
     ```

3. **Получите API ключи:**
   - Перейдите на [my.telegram.org](https://my.telegram.org) и получите `API_ID` и `API_HASH`.
   - Добавьте эти данные в файл `.env`.

4. **Запустите бота:**
   ```bash
   python3 main.py -a 2  # Запустить бота
   ```

### Ручная установка
1. **Linux:**
   ```bash
   sudo sh install.sh
   python3 -m venv venv
   source venv/bin/activate
   pip3 install -r requirements.txt
   cp .env-example .env
   nano .env  # Укажите свои API_ID и API_HASH
   python3 main.py
   ```

2. **Windows:**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   copy .env-example .env
   python main.py
   ```

### Установка с помощью Docker
1. **Скачайте и установите Docker:**

   - **Windows:**
     - Перейдите на [страницу загрузки Docker для Windows](https://www.docker.com/products/docker-desktop) и скачайте установщик.
     - Запустите установщик и следуйте инструкциям на экране.

   - **macOS:**
     - Перейдите на [страницу загрузки Docker для Mac](https://www.docker.com/products/docker-desktop) и скачайте Docker Desktop.
     - Откройте скачанный файл и перетащите Docker в папку "Приложения".

   - **Linux:**
     - В зависимости от вашего дистрибутива, выполните соответствующие команды:

       - **Ubuntu:**
         ```bash
         sudo apt update
         sudo apt install docker.io
         sudo systemctl start docker
         sudo systemctl enable docker
         ```

       - **Fedora:**
         ```bash
         sudo dnf install docker
         sudo systemctl start docker
         sudo systemctl enable docker
         ```

       - **Arch Linux:**
         ```bash
         sudo pacman -S docker
         sudo systemctl start docker
         sudo systemctl enable docker
         ```

2. **Проверьте установку Docker:**
   ```bash
   docker --version
   ```

3. **Настройте переменные окружения:**
   - Скопируйте файл `.env-example` в `.env` и настройте его с вашими `API_ID` и `API_HASH`.

4. **Скачайте и запустите проект:**
   ```bash
   git clone https://github.com/Mffff4/cityholderbot.git
   cd cityholder
   docker compose up -d
   ```

   Это скачает проект и запустит контейнер в фоновом режиме. Для просмотра логов используйте:
   ```bash
   docker compose logs -f
   ```

5. **Дополнительные команды:**
   - **Остановить проект:**
     ```bash
     docker compose down
     ```
   - **Перезапустить проект:**
     ```bash
     docker compose restart
     ```
   - **Обновить проект:**
     ```bash
     git pull
     docker compose up -d --build
     ```


---

## ⚙️ Настройки

| Настройка | Значение по умолчанию | Описание |
|-----------|------------------------|----------|
| API_ID | | Уникальный идентификатор приложения для Telegram API |
| API_HASH | | Хеш приложения для Telegram API |
| REF_ID |  | Реферальный ID для приглашений |
| SLEEP_TIME | [1900, 2000] | Диапазон времени сна между циклами (в секундах) |
| USE_PROXY_FROM_FILE | False | Использовать ли прокси из файла |
| FULL_LOG_INFO | False | Включить полное логирование |
| RANDOM_DELAY | [0.5, 3.0] | Диапазон случайной задержки (в секундах) |
| BROWSER_THREAD_TIMEOUT | [600, 1800] | Таймаут для потока браузера (в секундах) |
| BROWSER_CREATION_TIMEOUT | [120, 300] | Таймаут для создания браузера (в секундах) |
| MAX_RETRIES | 3 | Максимальное количество попыток |
| RETRY_DELAY | 5 | Задержка между попытками (в секундах) |
| PAGE_LOAD_DELAY | [2, 4] | Диапазон задержки загрузки страницы (в секундах) |
| CITY_BUTTON_CLICK_DELAY | [3, 5] | Диапазон задержки после клика по кнопке города (в секундах) |
| BUILD_BUTTON_CLICK_DELAY | [2, 4] | Диапазон задержки после клика по кнопке строительства (в секундах) |
| SCRIPT_TIMEOUT | [600, 1800] | Таймаут выполнения скрипта (в секундах) |
| PAGE_LOAD_TIMEOUT | 30 | Таймаут загрузки страницы (в секундах) |
| NAVIGATION_TIMEOUT | 30 | Таймаут навигации (в секундах) |
| SCRIPT_UPGRADE.max_execution_time | 180000 | Максимальное время выполнения скрипта апгрейда (в миллисекундах) |
| SCRIPT_UPGRADE.no_change_timeout | 30000 | Таймаут при отсутствии изменений (в миллисекундах) |
| SCRIPT_UPGRADE.click_delay | 2000 | Задержка между кликами (в миллисекундах) |
| SCRIPT_UPGRADE.post_click_delay | 1500 | Задержка после клика (в миллисекундах) |
| SCRIPT_UPGRADE.final_delay | 1000 | Финальная задержка (в миллисекундах) |
---

## 💰 Поддержка и донаты

Поддержите разработку с помощью криптовалют или платформ:

| Валюта               | Адрес кошелька                                                                       |
|----------------------|-------------------------------------------------------------------------------------|
| Bitcoin (BTC) | bc1qt84nyhuzcnkh2qpva93jdqa20hp49edcl94nf6 | 
| Ethereum (ETH) | 0xc935e81045CAbE0B8380A284Ed93060dA212fa83 | 
| TON | UQBlvCgM84ijBQn0-PVP3On0fFVWds5SOHilxbe33EDQgryz |
| Binance Coin (BNB) | 0xc935e81045CAbE0B8380A284Ed93060dA212fa83 | 
| Solana (SOL) | 3vVxkGKasJWCgoamdJiRPy6is4di72xR98CDj2UdS1BE | 
| Ripple (XRP) | rPJzfBcU6B8SYU5M8h36zuPcLCgRcpKNB4 | 
| Dogecoin (DOGE) | DST5W1c4FFzHVhruVsa2zE6jh5dznLDkmW | 
| Polkadot (DOT) | 1US84xhUghAhrMtw2bcZh9CXN3i7T1VJB2Gdjy9hNjR3K71 | 
| Litecoin (LTC) | ltc1qcg8qesg8j4wvk9m7e74pm7aanl34y7q9rutvwu | 
| Matic | 0xc935e81045CAbE0B8380A284Ed93060dA212fa83 | 
| Tron (TRX) | TQkDWCjchCLhNsGwr4YocUHEeezsB4jVo5 | 

---

## 📞 Контакты

Если у вас возникли вопросы или предложения:
- **Telegram**: [Присоединяйтесь к нашему каналу](https://t.me/+0C-gh0mKBzxiNzky)
---

## ⚠️ Дисклеймер

Данное программное обеспечение предоставляется "как есть", без каких-либо гарантий. Используя этот бот, вы принимаете на себя полную ответственность за его использование и любые последствия, которые могут возникнуть.

Автор не несет ответственности за:
- Любой прямой или косвенный ущерб, связанный с использованием бота
- Возможные нарушения условий использования сторонних сервисов
- Блокировку или ограничение доступа к аккаунтам

Используйте бота на свой страх и риск и в соответствии с применимым законодательством и условиями использования сторонних сервисов.

