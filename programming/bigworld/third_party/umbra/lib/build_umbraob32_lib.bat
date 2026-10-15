@echo off
rem Run from any directory - switches to this folder first. Used x86_64 cross tools of VS 2017
cd /d "%~dp0"
rem Generates umbraob32.lib (import library for umbraob32.dll).
rem Run ONCE from the VS2017 x86 Native Tools Command Prompt, in this folder:
lib /nologo /def:"umbraob32.def" /machine:x86 /out:"umbraob32.lib"
if errorlevel 1 (echo FAILED & exit /b 1)
echo umbraob32.lib generated.
