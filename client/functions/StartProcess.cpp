void StartProcess()
{
    std::string filePath = recv(1);
    std::replace(filePath.begin(), filePath.end(), '/', '\\');
    std::ifstream localFile(filePath);

    if (!localFile.is_open()) {
        send("invalid");
        return;

    } localFile.close(); send("valid");

    if (ShellExecuteA(NULL, "open", filePath.data(), NULL, NULL, 0)) {
        send("[+] Process Running");
    }
    else send("[!] Unable to Start Process");
}