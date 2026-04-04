```cmd
mkdir C:\AMBIENTEDEV
powershell -Command "Invoke-WebRequest -Uri 'https://updates.insomnia.rest/downloads/windows/latest?app=com.insomnia.app&source=website' -OutFile 'C:\AMBIENTEDEV\Insomnia.exe'"
powershell -Command "Invoke-WebRequest -Uri 'https://aka.ms/ssms/22/release/vs_SSMS.exe' -OutFile 'C:\AMBIENTEDEV\vs_SSMS.exe'"
powershell -Command "Invoke-WebRequest -Uri 'https://downloads.php.net/~windows/releases/archives/php-8.5.4-nts-Win32-vs17-x64.zip' -OutFile 'C:\AMBIENTEDEV\php.zip'"
powershell -Command "Invoke-WebRequest -Uri 'https://www.firefox.com/thanks/' -OutFile 'C:\AMBIENTEDEV\firefox.exe'"
powershell -Command "Invoke-WebRequest -Uri 'https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe?utm_source=docker&utm_medium=webreferral&utm_campaign=dd-smartbutton&utm_location=module&_gl=1*1vxjvbd*_gcl_au*MTgxNTk5NzAuMTc3NTA4MjAzMA..*_ga*MTE1NjIzMDYxNC4xNzQyMDQ3MjQz*_ga_XJWPQMJYHQ*czE3NzUxNzk0MjIkbzkkZzEkdDE3NzUxNzk0MzckajQ1JGwwJGgw' -OutFile 'C:\AMBIENTEDEV\docker.exe'"
powershell -Command "Invoke-WebRequest -Uri 'https://edgedl.me.gvt1.com/edgedl/release2/j0qc3/antigravity/stable/1.21.9-4905428782546944/windows-x64/Antigravity.exe' -OutFile 'C:\AMBIENTEDEV\Antigravity.exe'"
```
