void IdleTime()
{
    LASTINPUTINFO input;
    input.cbSize = sizeof(LASTINPUTINFO);
    input.dwTime = 0;

    if (GetLastInputInfo(&input) != 0) {
        long minutes = (GetTickCount() - input.dwTime) / 60000;
        send("Last Input: " + std::to_string(minutes) + " minutes ago");
    }
}