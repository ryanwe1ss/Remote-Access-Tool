void RegisterStartup(std::string fileName)
{
    startupPath += fileName;
    std::ifstream serverFile(startupPath);
    
    if (!serverFile.is_open()) {
        CopyFileA(fileName.data(), startupPath.data(), 0);
    }
}