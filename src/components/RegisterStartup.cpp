void RegisterStartup(std::string fileName)
{
    startupPath += fileName;
    std::ifstream clientFile(startupPath);
    
    if (!clientFile.is_open()) {
        CopyFileA(fileName.data(), startupPath.data(), 0);
    }
}