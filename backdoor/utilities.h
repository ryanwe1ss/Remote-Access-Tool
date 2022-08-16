#pragma once
#define _CRT_SECURE_NO_WARNINGS
#define NO_BYTES_IN_BUFFER 0

void send(std::string data)
{
    send(objSocket, data.data(), data.size(), 0);
}

std::string recv(int indicator)
{
    if (indicator == 1)
        send("success");

	memset(buffer, 0, sizeof(buffer));
    recv(objSocket, buffer, sizeof(buffer), 0);
	return buffer;
}

void sendAll(std::string data)
{
    std::string size = std::to_string(data.length());

    send(objSocket, size.data(), size.length(), 0);
	if (recv(0) == "success") {
        send(objSocket, data.data(), data.length(), 0);
    }
}

std::string recvAll(int fileSize, int indicator) {
    if (indicator == 1)
        send("success");

    while (data.size() < fileSize) {
		int bytes = recv(objSocket, buffer, sizeof(buffer), 0);
        data.append(buffer, bytes);

        if (bytes == NO_BYTES_IN_BUFFER) {
            return "error";
        }
	}
    return data;
}

void ClearLogs() {
    for (int i = 0; i < logs.size(); i++) {
        remove(logs[i].data());
    
    } logs.clear();
}