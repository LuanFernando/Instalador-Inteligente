```cmd
powershell -Command "if (!(Test-Path 'C:\inetpub\wwwroot\novosite')) { New-Item -ItemType Directory -Path 'C:\inetpub\wwwroot\novosite' -Force }"
echo ^<?php echo "Welcome to the new website."; ?^> > "C:\inetpub\wwwroot\novosite\index.php"
powershell -Command "& 'C:\Windows\System32\inetsrv\appcmd.exe' add site /name:'novosite' /bindings:http/*:80:local.novosite /physicalPath:'C:\inetpub\wwwroot\novosite'"
powershell -Command "attrib -r 'C:\Windows\System32\drivers\etc\hosts'"
powershell -Command "Add-Content -Path 'C:\Windows\System32\drivers\etc\hosts' -Value '127.0.0.1`tlocal.novosite'"
powershell -Command "Start-Process 'http://local.novosite'"
```
