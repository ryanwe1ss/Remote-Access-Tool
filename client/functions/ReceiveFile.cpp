void ReceiveFile()
{
	std::string fileName = recv(1), location = appdata + "\\" + fileName;
	int fileSize = atoi(recv(0).data());
	
	try {
		std::string fileData = recvAll(fileSize, 1);
		if (fileData == "error") {
			throw std::bad_alloc();
		
		} send("received");

		FILE *RemoteFile = fopen(location.data(), "wb");
		fwrite(fileData.data(), 1, fileData.size(), RemoteFile);
		fclose(RemoteFile);
	
	} catch (std::bad_alloc) {
		send("bad_alloc");
	}
}