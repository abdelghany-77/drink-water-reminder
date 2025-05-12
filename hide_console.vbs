Set WshShell = CreateObject("WScript.Shell")
CurrentDirectory = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
Command = "pythonw.exe main.py"
WshShell.CurrentDirectory = CurrentDirectory
WshShell.Run Command, 0, False