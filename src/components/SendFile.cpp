void SendFile()
{
	std::string filePath = recv(1);
    std::ifstream localFile(filePath.data(), std::ios::binary);

    if (!localFile.is_open()) {
        send("invalid");
        return;

    } send("valid");

    try {
        std::vector<char> buf(std::istreambuf_iterator<char>(localFile), {});
        std::string contents(buf.begin(), buf.end());

        localFile.close();
        sendAll(contents);
    
    } catch (std::bad_alloc) {
        sendAll("bad_alloc");
    }
}