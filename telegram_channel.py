import requests
from time import sleep


bot_token = "1959435613:AAErAtPTaOsVqHf1RSTEw5nI9CTw0KJdKYU"
channel_id = "@almaty_colesa_bot"


def telegram_bot_send_text(bot_message):
    """Отправляем сообщение в канал через телеграм бота"""
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + channel_id + '&parse_mode=Markdown&text=' + bot_message
    response = requests.get(send_text).json()
    sleep(0.1)
    return response


if __name__ == "__main__":
    telegram_bot_send_text("IMPORT TELEGRAM")
