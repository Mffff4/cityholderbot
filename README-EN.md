# City Holder Bot 🏠

> ⚠️ **Important Warning**: 
> This bot uses Selenium for automation, which can be an unstable solution. Future updates are not guaranteed. Use at your own risk.

[![Bot Link](https://img.shields.io/badge/Telegram-Bot_Link-blue?style=for-the-badge&logo=Telegram&logoColor=white)](https://t.me/cityholder/game?startapp=228618799)
[![Channel Link](https://img.shields.io/badge/Telegram-Channel_Link-blue?style=for-the-badge&logo=Telegram&logoColor=white)](https://t.me/+0C-gh0mKBzxiNzky)
[![Bot Collection](https://img.shields.io/badge/Bot_Collection-Link-blue?style=for-the-badge&logo=Telegram&logoColor=white)](https://t.me/+uF4lQD9ZEUE4NGUy)

---

## 📑 Table of Contents
1. [Description](#description)
2. [Key Features](#key-features)
3. [Installation](#installation)
   - [Quick Start](#quick-start)
   - [Manual Installation](#manual-installation)
4. [Settings](#settings)
5. [Support and Donations](#support-and-donations)
6. [Contacts](#contacts)

---

## 📜 Description
City Holder Bot is an automated bot for the City Holder game in Telegram. It helps manage the city, gather resources, and perform upgrades automatically.

## 🌟 Key Features
- 🏙️ Automatic city management
- 💰 Resource collection and tap execution
- 🏗️ Automatic building upgrades
- 🔄 Support for multiple accounts
- 🌐 Proxy support

---

## 🛠️ Installation

### Quick Start
1. **Download the project:**
   ```bash
   git clone https://github.com/Mffff4/cityholderbot.git
   cd cityholder
   ```

2. **Install dependencies:**
   - **Windows**:
     ```bash
     run.bat
     ```
   - **Linux**:
     ```bash
     run.sh
     ```

3. **Get API keys:**
   - Go to [my.telegram.org](https://my.telegram.org) and get `API_ID` and `API_HASH`.
   - Add this information to the `.env` file.

4. **Run the bot:**
   ```bash
   python3 main.py -a 2  # Start the bot
   ```

### Manual Installation
1. **Linux:**
   ```bash
   sudo sh install.sh
   python3 -m venv venv
   source venv/bin/activate
   pip3 install -r requirements.txt
   cp .env-example .env
   nano .env  # Specify your API_ID and API_HASH
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

---

## ⚙️ Settings

| Setting | Default Value | Description |
|---------|---------------|-------------|
| API_ID | | Unique application identifier for Telegram API |
| API_HASH | | Application hash for Telegram API |
| SLEEP_TIME | [1900, 2000] | Sleep time range between cycles (in seconds) |
| USE_PROXY_FROM_FILE | False | Use proxy from file |
| FULL_LOG_INFO | False | Enable full logging |
| HEADLESS | True | Run the browser in the background |
| RANDOM_DELAY | [0.5, 3.0] | Random delay range (in seconds) |
| BROWSER_THREAD_TIMEOUT | [600, 1800] | Timeout for browser thread (in seconds) |
| BROWSER_CREATION_TIMEOUT | [120, 300] | Timeout for browser creation (in seconds) |
| MAX_RETRIES | 3 | Maximum number of attempts |
| RETRY_DELAY | 5 | Delay between attempts (in seconds) |
| PAGE_LOAD_DELAY | [2, 4] | Page load delay range (in seconds) |
| CITY_BUTTON_CLICK_DELAY | [3, 5] | Delay range after clicking the city button (in seconds) |
| BUILD_BUTTON_CLICK_DELAY | [2, 4] | Delay range after clicking the build button (in seconds) |

---

## 💰 Support and Donations

Support the development with cryptocurrency or platforms:

| Currency               | Wallet Address                                                                       |
|------------------------|-------------------------------------------------------------------------------------|
| Bitcoin (BTC)          | bc1qt84nyhuzcnkh2qpva93jdqa20hp49edcl94nf6                                         | 
| Ethereum (ETH)         | 0xc935e81045CAbE0B8380A284Ed93060dA212fa83                                         | 
| TON                    | UQBlvCgM84ijBQn0-PVP3On0fFVWds5SOHilxbe33EDQgryz                                 |
| Binance Coin (BNB)     | 0xc935e81045CAbE0B8380A284Ed93060dA212fa83                                         | 
| Solana (SOL)          | 3vVxkGKasJWCgoamdJiRPy6is4di72xR98CDj2UdS1BE                                       | 
| Ripple (XRP)          | rPJzfBcU6B8SYU5M8h36zuPcLCgRcpKNB4                                                  | 
| Dogecoin (DOGE)       | DST5W1c4FFzHVhruVsa2zE6jh5dznLDkmW                                                | 
| Polkadot (DOT)        | 1US84xhUghAhrMtw2bcZh9CXN3i7T1VJB2Gdjy9hNjR3K71                                   | 
| Litecoin (LTC)        | ltc1qcg8qesg8j4wvk9m7e74pm7aanl34y7q9rutvwu                                       | 
| Matic                  | 0xc935e81045CAbE0B8380A284Ed93060dA212fa83                                         | 
| Tron (TRX)            | TQkDWCjchCLhNsGwr4YocUHEeezsB4jVo5                                                | 


---

## 📞 Contacts

If you have any questions or suggestions:
- **Telegram**: [Join our channel](https://t.me/+0C-gh0mKBzxiNzky)
