from flask import Flask, jsonify
import threading
import logging
import sys

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
cli = sys.modules['flask.cli']
cli.show_server_banner = lambda *x: None
app = Flask(__name__)

app.current = None
app.clients = None
app.clientInfo = None
app.VBSMessageBox = None

app.clients_lock = threading.Lock()

@app.route("/api/create-message/<message>")
def CreateMessage(message):
    app.VBSMessageBox(app.current, message)
    print(app.current)
    return jsonify({"status": "ok"})

@app.route("/api/get-clients")
def GetClients():
    return jsonify(app.clientInfo)

if __name__ == "__main__":
    app.run()