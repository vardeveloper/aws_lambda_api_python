import os
import json
import requests
from ftplib import FTP

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class Helpers(object):

    def __init__(self):
        pass

    @staticmethod
    def request(url, headers, payload):
        try:
            response = requests.post(url=url, headers=headers, json=payload)
            # data = response.json()
            return response
        except Exception as e:
            raise Exception("Error method request : {0}".format(e))

    @staticmethod
    def request_sendy(url, data):
        try:
            resp = requests.post(url=url, data=data)
            data = resp.text
            return data
        except Exception as e:
            # print(e)
            raise Exception("Error method request : {0}".format(e))

    @staticmethod
    def transfer_data(hostname, username, password, path, filename, path_remote=False):
        try:
            ftp = FTP(hostname)
            ftp.login(username, password)
            if path_remote:
                ftp.cwd(path_remote)
            ftp.storbinary('STOR ' + filename, open(path + filename, 'rb'))
            ftp.quit()
            print('Upload success:', filename)
            return True
        except Exception as e:
            # print(e)
            raise Exception("Error method transfer_data : {0}".format(e))

    @staticmethod
    def send_mail(subject, body):
        try:

            sender_email = 'notifications@ec.pe'
            receiver_email = 'victor.alcantara@fractalservicios.pe'

            message = MIMEMultipart()
            message['Subject'] = subject
            message['From'] = sender_email
            message['To'] = receiver_email

            text = 'Message test'

            part1 = MIMEText(text, "plain")
            part2 = MIMEText(body, "html")

            # message.attach(part1)
            message.attach(part2)

            relay = os.getenv('MAIL_RELAY')
            server = smtplib.SMTP(relay)
            server.sendmail(sender_email, receiver_email, message.as_string())

        except Exception as e:
            # print(e)
            raise Exception("Error method send_mail : {0}".format(e))

    @staticmethod
    def telegram_send_message(message):

        bot_chat_id = ""
        bot_token = ""
        url = "https://api.telegram.org/bot{}/".format(bot_token)

        send_text = url + 'sendMessage?chat_id=' + bot_chat_id + '&text=' + message
        response = requests.get(send_text)
        return response.json()
