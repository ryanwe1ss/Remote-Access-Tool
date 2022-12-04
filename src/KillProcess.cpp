void KillProcess()
{
    std::string process = recv(1), killCommand = "taskkill /im " + process + " /f", data;
    FILE* stream;

    killCommand.append(" 2>&1");
    stream = popen(killCommand.data(), "r");

    if (stream) {
        while (!feof(stream))
        if (fgets(buffer, sizeof(buffer), stream) != NULL) {
            data.append(buffer);
        
        } pclose(stream);
    }
    sendAll(data);
    fclose(stream);
}