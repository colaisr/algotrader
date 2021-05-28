set "params=%*"
cd /d "%~dp0" && ( if exist "%temp%\getadmin.vbs" del "%temp%\getadmin.vbs" ) && fsutil dirty query %systemdrive% 1>nul 2>nul || (  echo Set UAC = CreateObject^("Shell.Application"^) : UAC.ShellExecute "cmd.exe", "/k cd ""%~sdp0"" && %~s0 %params%", "", "runas", 1 >> "%temp%\getadmin.vbs" && "%temp%\getadmin.vbs" && exit /B )

schtasks /create /tn autorestart /tr "C:\Windows\System32\shutdown.exe -r" /sc daily /st 13:00 /f
@mklink "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\algotrader_autostart.lnk" "%~dp0..\win_start_all.bat"
exit