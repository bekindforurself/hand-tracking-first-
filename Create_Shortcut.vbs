Set oWS = WScript.CreateObject("WScript.Shell")
sLinkFile = oWS.SpecialFolders("Desktop") & "\SignLanguageTranslator.lnk"
Set oLink = oWS.CreateShortcut(sLinkFile)
oLink.TargetPath = "c:\Users\mohammed\ProjectStart\sign_lang_app\Run_Sign_App.bat"
oLink.WorkingDirectory = "c:\Users\mohammed\ProjectStart\sign_lang_app"
oLink.Description = "Run Arabic Sign Language Translator"
oLink.IconLocation = "shell32.dll, 25"
oLink.Save
