# City Holder Bot 🏠

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
7. [Disclaimer](#disclaimer)
8. [Using Proxies](#using-proxies)
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
| REF_ID |  | Referral ID for invitations |
| SLEEP_TIME | [1900, 2000] | Sleep time range between cycles (in seconds) |
| USE_PROXY_FROM_FILE | False | Use proxy from file |
| FULL_LOG_INFO | False | Enable full logging |
| CYCLE_WAIT_TIME | 10 | Wait time between cycles (in minutes) |
| RANDOM_DELAY | [0.5, 3.0] | Random delay range (in seconds) |
| BROWSER_THREAD_TIMEOUT | [600, 1800] | Timeout for browser thread (in seconds) |
| BROWSER_CREATION_TIMEOUT | [120, 300] | Timeout for browser creation (in seconds) |
| MAX_RETRIES | 3 | Maximum number of attempts |
| RETRY_DELAY | 5 | Delay between attempts (in seconds) |
| PAGE_LOAD_DELAY | [2, 4] | Page load delay range (in seconds) |
| CITY_BUTTON_CLICK_DELAY | [3, 5] | Delay range after clicking the city button (in seconds) |
| BUILD_BUTTON_CLICK_DELAY | [2, 4] | Delay range after clicking the build button (in seconds) |
| SCRIPT_TIMEOUT | [600, 1800] | Script execution timeout (in seconds) |
| PAGE_LOAD_TIMEOUT | 30 | Page load timeout (in seconds) |
| NAVIGATION_TIMEOUT | 30 | Navigation timeout (in seconds) |
| SCRIPT_UPGRADE.max_execution_time | 180000 | Maximum upgrade script execution time (in milliseconds) |
| SCRIPT_UPGRADE.no_change_timeout | 30000 | No change timeout (in milliseconds) |
| SCRIPT_UPGRADE.click_delay | 2000 | Delay between clicks (in milliseconds) |
| SCRIPT_UPGRADE.post_click_delay | 1500 | Post-click delay (in milliseconds) |
| SCRIPT_UPGRADE.final_delay | 1000 | Final delay (in milliseconds) |

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
---

## ⚠️ Disclaimer

This software is provided "as is" without any warranties of any kind. By using this bot, you accept full responsibility for its use and any consequences that may arise.

The author is not responsible for:
- Any direct or indirect damages related to the use of the bot
- Possible violations of third-party service terms of use
- Account blocking or access restrictions

Use the bot at your own risk and in compliance with applicable laws and third-party service terms of use.

---

## 🌐 Using Proxies

1. Create a `proxies.txt` file in the project root directory
2. Add proxies in any of the following formats:
   ```
   protocol://username:password@host:port
   username:password@host:port
   host:port:username:password
   host:port
   ```
   
   Examples:
   ```
   socks5://user:pass@1.2.3.4:1234
   http://admin:12345@proxy.example.com:8080
   1.2.3.4:1234:user:pass
   5.6.7.8:8080
   ```

3. In the `.env` file, set the parameter:
   ```
   USE_PROXY_FROM_FILE=True
   ```

Each proxy should be on a new line. Supported protocols: http, https, socks4, socks5.
