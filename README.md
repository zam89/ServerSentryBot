# ServerSentryBot
Linux server monitoring script for success and failure login (SSHD) via Telegram

## Features
- **Real-time monitoring**: Alerts you via Telegram when a failed login attempt is detected on your server.
- **Commands**:
  - `/start` : Lists all available commands.
  - `/monitor` : Begins real-time monitoring.
  - `/stop` : Stops the real-time monitoring.
  - `/last10fail` : Show the last 10 failed login attempts.
  - `/last10success` : Show the last 10 success login.
  - `/topip` : Shows the top IP addresses with failed attempts.
  - `/topuser` : Lists the most commonly tried usernames.
  - `/help` : Displays the help menu with available commands.

## Prerequisites
- A Telegram bot token (obtainable through BotFather on Telegram).
- Python 3.x installed on your server.
- The `requests` Python library (installable via pip).

## Installation
1. Clone the repository to your server:
    ```sh
    git clone https://github.com/zam89/ServerSentryBot.git
    ```

2. Navigate to the cloned directory:
    ```sh
    cd ServerSentryBot
    ```

3. Install the Request Python libraries:
    ```sh
    pip3 install requests
    ```

## Configuration
1. Open the `ServerSentryBot.py` script using a text editor of your choice.
2. Replace `YOUR_BOT_TOKEN` and `YOUR_CHAT_ID` with your actual bot token and your Telegram chat ID.

## Usage
To start the bot, you can use the following command:
```sh
sudo python3 ServerSentryBot.py
```

## Running as background process
For running the script in the background, you can use nohup, screen, or set it up as a systemd service as described in the script's documentation.
To setup via systemd, create `.service` file for in `/etc/systemd/system/`; e.g., `serversentry.service`:
```sh
[Unit]
Description=Python ServerSentryBot Script Service

[Service]
ExecStart=/usr/bin/python3.8 /<path>/ServerSentryBot/serversentrybot.py
User=root
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Reload systemd: Reload the systemd manager configuration:
```sh
sudo systemctl daemon-reload
```

### Enable service: Enable the service to start on boot:
```sh
sudo systemctl enable serversentry.service
```

### Start service: Start the service:
```sh
sudo systemctl start serversentry.service
```

### Check status: To check the status of your service:
```sh
sudo systemctl status serversentry.service
```

### Stopping: To stop the service:
```sh
sudo systemctl stop serversentry.service
```

## Acknowledgments
This bot was create due to need for simple, real-time monitoring of server security logs.

## Contributing
Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are greatly appreciated.
