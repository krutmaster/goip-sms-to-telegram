import aiosmtpd.controller
import email
import re
import base64
import telebot as tb
import asyncio
from settings import Settings


settings = Settings.open()
mail_id = settings.mail_id
bot = tb.TeleBot(settings.tg_token)


def send(mail_id, text):
    bot.send_message(chat_id=mail_id, text=text)


async def goip_data_send(data):
    if "error" in data:
        send(mail_id, "Error processing incoming message")
    else:
        message = "%s G%s\n%s" % (data["sender"], data["channel"], data["text"])
        send(mail_id, message)


@bot.message_handler(commands=["setgroupmail"])
def setgroupmail(message):
    global mail_id
    id = str(message.chat.id)

    if mail_id != id:

        try:
            input_password = message.text.split()[1]

            if input_password == settings.password:
                mail_id = id
                settings.set_mail_id(mail_id)
                bot.send_message(id, 'Данная группа установлена по умолчанию для sms.')
            else:
                bot.send_message(id, 'Неправильный пароль, попробуй ещё раз.')

        except:
            bot.send_message(id, 'Команда введена неправильно, попробуйте ещё раз.')

    
class GOIPSMTPHandler:
    def __init__(self):
        self.regexp = re.compile("SN:(?P<sn>.+)\s{1}Channel:(?P<channel>[0-9]+)\s{1}Sender:(?P<time>[0-9-:\s]+),(?P<sender>.+?),(?P<text>.*)")


    async def handle_DATA(self, server, session, envelope):
        print("Got a message from goip")
        msg = envelope.content.decode()
        text_b64 = email.message_from_string(msg).get_payload()
        text = base64.b64decode(text_b64).decode()
        result = self.regexp.match(text).groupdict()
        if len(result) > 0:
            data = result
        else:
            data = {"error": True}
        asyncio.create_task(goip_data_send(data))
        return '250 OK'

print("Starting service...")

goip_handler = GOIPSMTPHandler()
goip_server = aiosmtpd.controller.Controller(goip_handler, hostname='0.0.0.0', port=25)
goip_server.start()

asyncio.get_event_loop().run_forever()
bot.polling(none_stop=True)
