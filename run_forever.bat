@echo off
:loop
echo Starting Trading Bot...
python main.py
echo Bot crashed. Restarting in 5 seconds...
timeout /t 5
goto loop