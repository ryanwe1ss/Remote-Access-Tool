void DeleteFile()
{
    std::string filePath = recv(1);
    std::ifstream localFile(filePath);

    if (!localFile.is_open()) {
        send("invalid");
        return;

    } localFile.close(); send("valid");

    if (remove(filePath.data()) != 0) {
        send("[!] Unable to Delete File");
    }
    else send("[+] File Deleted");
}