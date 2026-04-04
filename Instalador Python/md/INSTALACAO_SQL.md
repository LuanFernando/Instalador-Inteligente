```powershell
New-Item -Path "C:\Installers" -ItemType Directory -Force
Invoke-WebRequest -Uri "https://go.microsoft.com/fwlink/?linkid=866658" -OutFile "C:\Installers\SQLServerSetup.exe"
Start-Process -FilePath "C:\Installers\SQLServerSetup.exe" -ArgumentList "/Q /Action=Install /InstanceName=MSSQLSERVER /Features=SQL /SecurityMode=SQL /SAPWD='SenhaForte@server' /SQLSYSADMINACCOUNTS='Administrators' /IAcceptSQLServerLicenseTerms" -Wait
Invoke-WebRequest -Uri "https://aka.ms/ssms/22/release/vs_SSMS.exe" -OutFile "C:\Installers\SSMS_Setup.exe"
Start-Process -FilePath "C:\Installers\SSMS_Setup.exe" -ArgumentList "/install /quiet /norestart" -Wait
Start-Sleep -Seconds 30
& "C:\Program Files\Microsoft SQL Server\Client SDK\ODBC\170\Tools\Binn\SQLCMD.EXE" -S . -U sa -P SenhaForte@server -Q "CREATE DATABASE MEUBANCO;"
```
