std::string getPath(std::string const& path)
{
    std::string::size_type pos = path.find(" -");
    if (pos != std::string::npos) {
        return path.substr(0, pos);
    }
    return path;
}

int find(std::string file, std::string filter)
{
    transform(file.begin(), file.end(), file.begin(), ::tolower);
    transform(filter.begin(), filter.end(), filter.begin(), ::tolower);

    if (file.find(filter) != std::string::npos) {
        return 0;
    }
    return 1;
}

void ViewFiles()
{
    std::string folder = recv(1);
    std::string path, filter, data;
    bool filtered = true;

    path = getPath(folder);
    filter = folder.substr(folder.find(" -") + 1);

    if (filter.find("-") == std::string::npos) {
        filtered = false;
    
    } filter.erase(std::remove(filter.begin(), filter.end(), '-'), filter.end());

    struct dirent* entry;
    DIR* dir = opendir(path.data());

    if (!dir) {
        send("invalid");
        return;

    } send("valid");

    while ((entry = readdir(dir)) != NULL) {
        std::string file = entry->d_name;

        if (!strcmp(file.data(), ".") || !strcmp(file.data(), "..")) {
            continue;
        }

        if (filtered) {
            if (find(file, filter) == 0) {
                data += file; data += "\n";
            }
        
        } else { data += file; data += "\n"; }

    } closedir(dir); sendAll(data);
}