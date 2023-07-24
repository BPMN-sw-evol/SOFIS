@echo off

REM Check if the help argument is provided
if /i "%~1"=="-h" goto show_help

REM Check if no arguments are provided
if "%~1"=="" (
    set /p API_KEY="API Key: "
    set /p SEARCH_TITLE="Search Title: "
    set /p UPPER_DATE="Upper date (DD-MM-YYYY): "
    set /p DIRECTORY="Directory to save CSV files: "
)

REM Check if all arguments are provided
if "%API_KEY%"=="" (
    echo Error: API Key not provided.
    exit /b 1
)

if "%SEARCH_TITLE%"=="" (
    echo Error: Search Title not provided.
    exit /b 1
)

if "%UPPER_DATE%"=="" (
    echo Error: Upper date not provided.
    exit /b 1
)

if "%DIRECTORY%"=="" (
    echo Error: Directory not provided.
    exit /b 1
)

REM Code to execute the script with the provided arguments
python STACK_QUERY_CSV.py -k "%API_KEY%" -i "%SEARCH_TITLE%" -s "%UPPER_DATE%" -d "%DIRECTORY%"

REM Pause to keep the console open after the execution
pause

exit /b

REM Method to show the command help
:show_help
echo Usage: %~nx0 [OPTIONS]
echo.
echo OPTIONS:
echo   -k, --key            StackExchange API Key (required)
echo                         Example: -k "ahhBNdmxDJ5zP2dxaJvCHw(("
echo.
echo   -i, --intitle        StackOverflow Search Title (required)
echo                         Example: -i "camunda"
echo.
echo   -s, --upper-date     Upper date to filter discussions (DD-MM-YYYY) (required)
echo                         Example: -s "12-06-2023"
echo.
echo   -d, --directory      Directory to save CSV files (required)
echo                         Example: -d "G:\Monitorias"
echo.
echo   -h, --help           Show help
echo.
exit /b