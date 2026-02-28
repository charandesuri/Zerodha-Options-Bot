@echo off
cd /d C:\trading_bot
python login.py
timeout /t 3
start run_forever.bat