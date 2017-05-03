from pprint import pprint
import requests
from requests.auth import HTTPBasicAuth
import json
import sys
try:
    from flask import Flask
    from flask import request
except ImportError as e:
    print(e)
    print("Looks like 'flask' library is missing.\n"
          "Type 'pip3 install flask' command to install the missing library.")
    sys.exit()


bearer = "YTVkYTExYjctN2NmZS00ZGI5LTk1YWMtMTNjNzJjMDNiN2NmOWM4NTc0MmMtYmRm" # BOT'S ACCESS TOKEN
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json; charset=utf-8",
    "Authorization": "Bearer " + bearer
}


def send_spark_get(url, payload=None,js=True):

    if payload == None:
        request = requests.get(url, headers=headers)
    else:
        request = requests.get(url, headers=headers, params=payload)
    if js == True:
        request= request.json()
    return request


def send_spark_post(url, data):

    request = requests.post(url, json.dumps(data), headers=headers).json()
    return request


def help_me():

    return "Sure! I can help. Below are the commands that I understand:<br/>" \
           "`Help me` - I will display what I can do.<br/>" \
           "`Hello` - I will display my greeting message<br/>" \
           "`Repeat after me` - I will repeat after you <br/>" \
           "`SMS + Number in E164 format + Message` - I will send an SMS<br/>" \

def greetings():

    return "Hi my name is %s.<br/>" \
           "Type `Help me` to see what I can do.<br/>" % bot_name


def sms(numbertodial, message):
    token = '50504e51704b694851516f6e497a47697449505857517163594c6f564855576b6a6463786e4466716e417a78'
    url = 'https://api.tropo.com/1.0/sessions'
    user = "pierrerousseau1"
    password="Orange82"
    data={'token':token,'numbertodial':numbertodial,'msg':message}
    resp = requests.post(url,
                     data,
                     auth=HTTPBasicAuth(user,password))
    print (resp)
    msg = "SMS sent to '"+numbertodial+"' with this message '"+message+"'."
    return msg

app = Flask(__name__)
@app.route('/', methods=['GET', 'POST'])
def spark_webhook():
    if request.method == 'POST':
        webhook = request.get_json(silent=True)
        if webhook['data']['personEmail']!= bot_email:
            pprint(webhook)
        if webhook['resource'] == "memberships" and webhook['data']['personEmail'] == bot_email:
            send_spark_post("https://api.ciscospark.com/v1/messages",
                            {
                                "roomId": webhook['data']['roomId'],
                                "markdown": (greetings() +
                                             "**Note This is a group room and you have to call "
                                             "me specifically with `@%s` for me to respond**" % bot_name)
                            }
                            )
        msg = None
        if "@sparkbot.io" not in webhook['data']['personEmail']:
            result = send_spark_get(
                'https://api.ciscospark.com/v1/messages/{0}'.format(webhook['data']['id']))
            in_message = result.get('text', '').lower()
            in_message = in_message.replace(bot_name.lower() + " ", '')
            if in_message.startswith('help me'):
                msg = help_me()
            elif in_message.startswith('hello'):
                msg = greetings()
            elif in_message.startswith('sms'):
                content = in_message.split('sms ')[1]
                contentLen=len(content)
                numbertodial=content[0:11]
                message = content[12:contentLen]
                print(numbertodial)
                print(message)
                msg = sms(numbertodial, message)
            elif in_message.startswith("repeat after me"):
                message = in_message.split('repeat after me ')[1]
                if len(message) > 0:
                    msg = "{0}".format(message)
                else:
                    msg = "I did not get that. Sorry!"
            else:
                msg = "Sorry, but I did not understand your request. Type `Help me` to see what I can do"
            if msg != None:
                send_spark_post("https://api.ciscospark.com/v1/messages",
                                {"roomId": webhook['data']['roomId'], "markdown": msg})
        return "true"
    elif request.method == 'GET':
        message = "<center><img src=\"http://bit.ly/SparkBot-512x512\" alt=\"Spark Bot\" style=\"width:256; height:256;\"</center>" \
                  "<center><h2><b>Congratulations! Your <i style=\"color:#ff8000;\">%s</i> bot is up and running.</b></h2></center>" \
                  "<center><b><i>Please don't forget to create Webhooks to start receiving events from Cisco Spark!</i></b></center>" % bot_name
        return message

def main():
    global bot_email, bot_name
    if len(bearer) != 0:
        test_auth = send_spark_get("https://api.ciscospark.com/v1/people/me", js=False)
        if test_auth.status_code == 401:
            print("Looks like provided access toke is not correct. \n"
                  "Please review it and make sure it belongs to your bot account.\n"
                  "Do not worry if you have lost the access token. "
                  "You can always go to https://developer.ciscospark.com/apps.html "
                  "URL and generate a new access token.")
            sys.exit()
        if test_auth.status_code == 200:
            test_auth = test_auth.json()
            bot_name = test_auth.get("displayName","")
            bot_email = test_auth.get("emails","")[0]
    else:
        print("'bearer' variable is empty! \n"
              "Please populate it with bot's access token and run the script again.\n"
              "Do not worry if you have lost the access token. "
              "You can always go to https://developer.ciscospark.com/apps.html "
              "URL and generate a new access token.")
        sys.exit()

    if "@sparkbot.io" not in bot_email:
        print("You have provided access token which does not belong to your bot.\n"
              "Please review it and make sure it belongs to your bot account.\n"
              "Do not worry if you have lost the access token. "
              "You can always go to https://developer.ciscospark.com/apps.html "
              "URL and generate a new access token.")
        sys.exit()
    else:
        app.run(host='localhost', port=8080)

if __name__ == "__main__":
    main()
