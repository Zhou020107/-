Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
appDir = fso.GetParentFolderName(WScript.ScriptFullName)
WshShell.CurrentDirectory = appDir

pythonExe = "C:\Users\zhoumingrui\AppData\Local\Programs\Python\Python313\python.exe"
streamlitExe = fso.GetParentFolderName(pythonExe) & "\Scripts\streamlit.exe"

If Not fso.FileExists(streamlitExe) Then
    MsgBox "找不到 streamlit，请先运行 pip install streamlit"
    WScript.Quit
End If

cmd = "cmd /c """ & streamlitExe & """ run app.py --server.headless true"
WshShell.Run cmd, 0, False
