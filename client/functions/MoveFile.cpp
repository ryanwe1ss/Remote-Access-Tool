void MoveFile()
{
    std::string filePath = recv(0);
    std::string directory = recv(1);

    std::ifstream localFile(filePath);
    if (localFile.is_open()) {
        if (GetFileAttributesA(directory.data()) != INVALID_FILE_ATTRIBUTES) {

            send("file");
            localFile.close();

            std::string newLocation = directory + "/" + filePath.substr(filePath.find_last_of("/\\") + 1);
            MoveFileA(filePath.data(), newLocation.data());

            return;
        
        } else send("invalid-directory");
    
    } else send("invalid-file");

    localFile.close();
}