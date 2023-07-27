void WakeComputer()
{
  POINT pt;
  INPUT input;

  GetCursorPos(&pt);
  input.type = INPUT_MOUSE;
  input.mi.mouseData = 0;
  input.mi.dx = 0;
  input.mi.dy = 0;
  input.mi.dwFlags = MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_MOVE;

  SendInput(1, &input, sizeof(input));
  Sleep(5);

  input.mi.dx = 65535;
  input.mi.dy = 65535;
  input.mi.dwFlags = MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_MOVE;
  
  SendInput(1, &input, sizeof(input));
  Sleep(5);

  SetCursorPos(pt.x, pt.y);
  SetThreadExecutionState(ES_DISPLAY_REQUIRED | ES_SYSTEM_REQUIRED);

  send("success");
}