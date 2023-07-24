@echo off

REM Check if the help argument is provided
if /i "%~1"==="-h" (
    call :show_help
    exit /b
)

REM Check if no arguments are provided
if "%~1"=="" (
    set /p API_KEY="API Key: "
    set /p SEARCH_TITLE="Search Title: "
    set /p DATABASE="Database name: "
    set /p USER="Database username: "
    set /p PASSWORD="Database user password: "
    set /p UPPER_DATE="Upper date (DD-MM-YYYY): "
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

if "%DATABASE%"=="" (
    echo Error: Database name not provided.
    exit /b 1
)

if "%USER%"=="" (
    echo Error: Database username not provided.
    exit /b 1
)

if "%PASSWORD%"=="" (
    echo Error: Database user password not provided.
    exit /b 1
)

if "%UPPER_DATE%"=="" (
    echo Error: Upper date not provided.
    exit /b 1
)

REM Code to execute the script with the provided arguments
python "STACK_QUERY_DB.py" -k "%API_KEY%" -i "%SEARCH_TITLE%" -d "%DATABASE%" -u "%USER%" -p "%PASSWORD%" -f "%UPPER_DATE%"

REM Pause to keep the console open after the execution
pause

exit /b

REM Method to show the command help
:show_help
echo Usage: %~nx0 [OPTIONS]
echo OPTIONS:
echo   -k, --key            StackExchange API Key (required)
echo                         Example: -k "ahhBNdmxDJ5zP2dxaJvCHw(("
echo.
echo   -i, --intitle        StackOverflow Search Title (required)
echo                         Example: -i "camunda"
echo.
echo   -d, --database       Database name (required)
echo                         Example: -d "mydatabase"
echo.
echo   -u, --user           Database username (required)
echo                         Example: -u "myuser"
echo.
echo   -p, --password       Database user password (required)
echo                         Example: -p "mypassword"
echo.
echo   -f, --upper-date     Upper date to filter discussions (DD-MM-YYYY) (required)
echo                         Example: -f "12-06-2023"
echo.
echo   -h, --help           Show help
echo.
exit /b
