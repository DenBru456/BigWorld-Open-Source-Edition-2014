@ECHO OFF

SET RES_PATH=

echo Enter tutorial name (e.g. "basic_npc" without quotes), or nothing for default.
SET /P RES_PATH=] 


IF "%RES_PATH%"=="" ( 
SET RES_PATH=res
) ELSE (
SET RES_PATH=res_%RES_PATH%
)

IF NOT EXIST %~dp0%RES_PATH% (
ECHO Resources for specified tutorial do not exist.
PAUSE
) ELSE (
if EXIST ..\bigworld\bin\win32\bwclient.exe (start ..\bigworld\bin\win32\bwclient.exe --res %~dp0%RES_PATH%;../../../bigworld/res) ELSE (start ..\bigworld\bin\win32\bwclient_indie.exe --res %~dp0%RES_PATH%;../../../bigworld/res) 
)
