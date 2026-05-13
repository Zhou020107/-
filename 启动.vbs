Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
appDir = fso.GetParentFolderName(WScript.ScriptFullName)

pythonExe = "C:\Users\zhoumingrui\AppData\Local\Programs\Python\Python313\python.exe"
exeDir = fso.GetParentFolderName(pythonExe)
streamlitExe = exeDir & "\Scripts\streamlit.exe"

If Not fso.FileExists(streamlitExe) Then
    MsgBox "找不到 streamlit.exe"
    WScript.Quit
End If

cmd = "cmd /c cd /d """ & appDir & """ && """ & streamlitExe & """ run app.py --server.headless true"
WshShell.Run cmd, 0, False

WScript.Sleep 4000
WshShell.Run "http://localhost:8501"
