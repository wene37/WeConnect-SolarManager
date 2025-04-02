import json
import os
import re

from flask import Flask, render_template, request

from Helper import Helper

configParser = Helper.loadConfig()
port = configParser.getint("WebApp", "Port")
publicKey = configParser.get("WebApp", "WebPushPublicKey")

templateDir = os.path.join(os.path.dirname(__file__), "templates")
staticDir = os.path.join(os.path.dirname(__file__), "static")
app = Flask("WeConnect-SolarManager", template_folder=templateDir, static_folder=staticDir)

def getLogs() -> str:

    logEntries = []
    logLines = Helper.getLogEntries()

    for line in logLines:

        dateMatch = re.match(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{1,3}", line)

        if dateMatch == None:
            logEntries[-1] += "<br/>" + line
        else:
            dateMatchLength = len(dateMatch.group(0))
            logEntries.append("<span class='logTime'>" + line[0:dateMatchLength] + "</span>" + line[dateMatchLength:])

    logEntries.reverse()

    return '<br/>'.join(logEntries)

@app.route('/api/pushnotification', methods=['POST'])
def pushNotification():

    data = request.json
    endpoint = data["endpoint"]
    auth = data["auth"]
    p256dh = data["p256dh"]

    pushNotifications = Helper.loadPushNotifications()
    alreadyDefined = False

    for device in pushNotifications["devices"]:
        if device["endpoint"] == endpoint and device["auth"] == auth and device["p256dh"] == p256dh:
            alreadyDefined = True
            break

    if alreadyDefined == False:
        pushNotifications["devices"].append({"endpoint": endpoint, "auth": auth, "p256dh": p256dh})
        Helper.savePushNotifications(pushNotifications)

    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

@app.route('/')
def index():
    return render_template('index.html', PublicKey=publicKey, LogOutput=getLogs())

if __name__ == '__main__':
    app.run(debug=False, ssl_context='adhoc', port=port, host='0.0.0.0')
