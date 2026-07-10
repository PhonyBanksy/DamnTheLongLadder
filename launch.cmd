@echo off
powershell -Command "Start-Process powershell -Verb RunAs -ArgumentList '-NoExit','-Command','cd D:\pi; ssh -i \"$env:APPDATA\talon\user\pisudo\" pi@adguard.local'"
powershell -Command "Start-Process cmd -Verb RunAs -ArgumentList '/k','cd /d D:\pi'"