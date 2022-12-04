void VBSMessageBox()
{
	std::string message = recv(1);
	std::string location = appdata + "\\msg.vbs";

	std::ofstream VBS_FILE(location);
	VBS_FILE << "MsgBox (\"" + message + "\"), 64, \"\"";
	VBS_FILE.close();

	if (ShellExecuteA(NULL, "open", location.data(), NULL, NULL, 0)) {
		send("[+] Message Sent");
	}
	else send("[!] Unable to Display Message");

	logs.push_back(location);
}