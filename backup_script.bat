@echo off
set DATE=%DATE:~-4,4%-%DATE:~-10,2%-%DATE:~-7,2%
set BACKUP_DIR=D:\Download\HugginFace\VenusChatbot\Venus_project
set DATABASE_FILE=D:\Download\HugginFace\VenusChatbot\Venus_project\db.sqlite3
set BACKUP_FILE=%BACKUP_DIR%db_backup_%DATE%.sqlite3

copy "%DATABASE_FILE%" "%BACKUP_FILE%"
