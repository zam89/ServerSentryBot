import time
import re
import requests
from collections import Counter
from threading import Thread

# Replace with your Telegram Bot Token and Chat ID
bot_token = 'YOUR_BOT_TOKEN'
chat_id = 'YOUR_CHAT_ID'
log_file_path = '/var/log/auth.log'

# Global flag to control monitoring
monitoring_active = False

# Function to send messages to Telegram
def send_telegram_message(message):
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'Markdown'
    }
    response = requests.post(url, json=payload)
    return response.json()

# Function to process updates from Telegram
def process_updates(last_update_id):
    global monitoring_active
    
    url = f'https://api.telegram.org/bot{bot_token}/getUpdates?offset={last_update_id + 1}'
    response = requests.get(url)
    updates = response.json().get('result', [])
    
    for update in updates:
        last_update_id = update['update_id']
        message = update.get('message', {})
        text = message.get('text', '')
        from_id = message.get('from', {}).get('id')

        if from_id == int(chat_id):  # Commands from the authorized user
            if text == '/start':
                robot_icon = u'\U0001F916'
                send_telegram_message(f"Welcome to ServerSentryBot {robot_icon}\n"
                                      "Menu:\n"
                                      "/monitor - Start monitoring in real-time\n"
                                      "/stop - Stop the real-time monitoring\n"
                                      "/last10fail - Show the last 10 failed login attempts\n"
                                      "/last10success - Show the last 10 success login\n"
                                      "/topip - Show the top IP addresses with failed attempts\n"
                                      "/topuser - Show the top usernames attempted\n"
                                      "/help - Show help menu")
            elif text == '/last10fail':
                last10_fail()
            elif text == '/last10success':
                last10_success()
            elif text == '/monitor':
                monitoring_active = True
                send_telegram_message("Monitoring mode activated.")
                Thread(target=check_logins).start()
            elif text == '/stop':
                monitoring_active = False
                send_telegram_message("Monitoring mode deactivated.")
            elif text == '/topip':
                send_top_ips()
            elif text == '/topuser':
                send_top_users()
            elif text == '/help':
                menu_icon = u'\U0001F4D1'
                send_telegram_message(f"{menu_icon} Help menu:\n"
                                      "/monitor - Start monitoring in real-time\n"
                                      "/stop - Stop the real-time monitoring\n"
                                      "/last10fail - Show the last 10 failed login attempts\n"
                                      "/last10success - Show the last 10 success login\n"
                                      "/topip - Show the top IP addresses with failed attempts\n"
                                      "/topuser - Show the top usernames attempted")

    return last_update_id

# Function to search for 10 fail login
def last10_fail():
    with open(log_file_path, "r") as log_file:
        logs = log_file.readlines()

    failed_attempts = [log for log in logs if "Failed password" in log]
    fail_icon = u'\u26A0'
    message = f"{fail_icon} Last 10 failed login attempts {fail_icon}\n" + "\n".join(failed_attempts[-10:])  # Send the last 10 attempts
    send_telegram_message(message)

# Function to search for 10 success login
def last10_success():
    with open(log_file_path, "r") as log_file:
        logs = log_file.readlines()

    success_attempts = [log for log in logs if "Accepted password" in log]
    success_icon = u'\U0001F511'
    message = f"{success_icon} Last 10 success login {success_icon}\n" + "\n".join(success_attempts[-10:])  # Send the last 10 attempts
    send_telegram_message(message)

# Function to find top 10 IP addresses with failed login attempts
def send_top_ips():
    with open(log_file_path, "r") as log_file:
        logs = log_file.readlines()

    ip_addresses = [re.search(r'(\d+\.\d+\.\d+\.\d+)', log).group(0) for log in logs if "Failed password" in log]
    top_ips = Counter(ip_addresses).most_common(10)  # Adjust the number as needed
    top_icon = u'\U0001F51D'
    bullet_icon = u'\u2022'
    message = f"{top_icon} Top IP addresses with failed login attempts {top_icon}\n" + "\n".join(f"{bullet_icon} {ip}: {count} times" for ip, count in top_ips)
    send_telegram_message(message)

# Function to find top 10 usernames with failed login attempts
def send_top_users():
    with open(log_file_path, "r") as log_file:
        logs = log_file.readlines()

    usernames = [re.search(r'Failed password for (invalid user )?(.*?) from', log).group(2) for log in logs if "Failed password" in log]
    top_users = Counter(usernames).most_common(10)  # Adjust the number as needed
    top_icon = u'\U0001F51D'
    bullet_icon = u'\u2022'
    message = f"{top_icon} Top usernames with failed login attempts {top_icon}\n" + "\n".join(f"{bullet_icon} {user}: {count} times" for user, count in top_users)
    send_telegram_message(message)

# Function to monitor logins in real-time
def check_logins():
    global monitoring_active
    specific_user = 'root'  # Replace with the username you want to monitor
    with open(log_file_path, "r") as log_file:
        log_file.seek(0, 2)  # Go to the end of the file
        while monitoring_active:
            line = log_file.readline()
            if not line:
                time.sleep(0.1)  # Sleep briefly
                continue
            # Check if both "Failed password" and the specific user are in the log line
            if "Failed password" in line and specific_user in line:
                ip = re.search(r'(\d+\.\d+\.\d+\.\d+)', line).group(0)
                # Find the exact match for the username
                user_match = re.search(r'Failed password for (invalid user )?(.*?) from', line)
                if user_match:
                    user = user_match.group(2)
                    if user == specific_user:
                        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                        
                        # Emojis for the alert message
                        globe_icon = u'\U0001F30E'   # Earth globe emoji
                        person_icon = u'\U0001F464'  # Bust in silhouette emoji
                        clock_icon = u'\U0001F553'   # Clock face three o'clock emoji
                        fail_icon = u'\u26A0'        # Warning emoji
                        
                        message = (f'{fail_icon} Alert! Failed login detected for user {specific_user}! {fail_icon}\n'
                                   f'{globe_icon} IP: {ip}\n'
                                   f'{person_icon} Username: {user}\n'
                                   f'{clock_icon} Timestamp: {timestamp}')
                        send_telegram_message(message)

if __name__ == '__main__':
    last_update_id = 0

    # Main loop
    while True:
        last_update_id = process_updates(last_update_id)
        time.sleep(1)
