@echo off
echo Please wait while the source code is checked. A log file will be created in
echo this same directory, containing the missing strings, if any.
echo This might take a few minutes to complete.

echo -------------------------------------------------------------------------------- >> english_missing_strings.log
python chk_lang.py -en >> english_missing_strings.log
