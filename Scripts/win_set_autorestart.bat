schtasks /create /tn autorestart /tr "C:\Windows\System32\shutdown.exe -r" /sc daily /st 13:00 /f
schtasks /create /tn autostart_trader /tr win_start_all.bat /sc onstart /f