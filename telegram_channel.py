import requests
from time import sleep


bot_token = "BOT_TOKEN"
channel_id = "@channel_name"


def telegram_bot_send_text(bot_message):
    """Отправляем сообщение в канал через телеграм бота"""
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + channel_id + '&parse_mode=Markdown&text=' + bot_message
    response = requests.get(send_text).json()
    sleep(0.1)
    return response


if __name__ == "__main__":
    telegram_bot_send_text("IMPORT TELEGRAM")
