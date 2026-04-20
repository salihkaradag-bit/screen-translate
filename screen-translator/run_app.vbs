Set WshShell = CreateObject("WScript.Shell")
appPath = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName) & "\dist\ScreenTranslator.exe"
WshShell.Run """" & appPath & """", 0, False
