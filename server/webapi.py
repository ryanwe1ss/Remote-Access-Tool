from flask import Flask, jsonify, request
import threading
import logging
import sys

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
cli = sys.modules['flask.cli']
cli.show_server_banner = lambda *x: None
api = Flask(__name__)

routes = [
    "/api/create-message/<message>",
    "/api/get-client",
]

api.connection = None
api.clients = None
api.clientInfo = None
api.VBSMessageBox = None

api.clients_lock = threading.Lock()

# MIDDLEWARE
@api.before_request
def before_request():
    if (request.path in routes):
        if (api.connection == None):
            return jsonify({"status": "error", "message": "Not connected to a client."})

# POST ROUTES
@api.post("/api/create-message/<message>")
def CreateMessage(message):
    response = api.VBSMessageBox(api.connection, message)
    if (response):
        return jsonify({"status": "sent", "message": message})
    else:
        return jsonify({"status": "error", "message": "Failed to send message."})
    
@api.post("/api/connect-client/<connectionId>")
def ConnectClient(connectionId):
    connectionId = int(connectionId)

    if (len(api.clients) > connectionId):
        api.connection = connectionId
        return jsonify({"status": 201, "message": "Client connected."})
    else:
        return jsonify({"status": 404, "message": "Client not found."})
    
@api.post("/api/disconnect-client")
def DisconnectClient():
    api.connection = None
    return jsonify({"status": "disconnected", "message": "Client disconnected."})

# GET ROUTES
@api.get("/api/get-clients")
def GetClients():
    return jsonify(api.clientInfo)

@api.get('/api/get-client')
def GetClient():
    return jsonify(api.SystemInformation(api.connection))

if __name__ == "__main__":
    api.run()