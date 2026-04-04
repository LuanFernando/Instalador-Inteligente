```powershell
mkdir C:\SIGER
powershell -Command "New-Item -ItemType Directory -Path 'C:/SIGER' -Force; Invoke-WebRequest -Uri 'http://192.168.15.35:3232/assets/SIGER.zip' -OutFile 'C:/SIGER/SIGER.zip'; Expand-Archive -Path 'C:/SIGER/SIGER.zip' -DestinationPath 'C:/SIGER' -Force"
powershell -Command "Start-Process -FilePath 'C:/SIGER/SIGER.exe' -WorkingDirectory 'C:/SIGER'"
```
