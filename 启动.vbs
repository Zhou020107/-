Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
appDir = fso.GetParentFolderName(WScript.ScriptFullName)
WshShell.CurrentDirectory = appDir
WshShell.Run "cmd /c streamlit run app.py --server.headless true > nul 2>&1", 0, False
