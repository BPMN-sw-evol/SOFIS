@echo off

REM Check if the help argument is provided
if /i "%~1"=="-h" goto show_help

REM Check if -r argument is provided to request arguments one by one
if /i "%~1"=="-r" goto request_arguments

REM Check if all required arguments are provided
if "%~7"=="" (
    echo Error: Insufficient arguments. Please provide all required parameters.
    echo Usage: %~nx0 -k "API Key" -i "Search Title" -d "Database name" -u "Database username" -p "Database user password" -f "Upper date (DD-MM-YYYY)" [-r]
    exit /b 1
)

REM Parse the command line arguments
set "API_KEY=%~1"
set "SEARCH_TITLE=%~2"
set "DATABASE=%~3"
set "USER=%~4"
set "PASSWORD=%~5"
set "UPPER_DATE=%~6"

REM Code to execute the script with the provided arguments
python "STACK_QUERY_DB.py" -k "%API_KEY%" -i "%SEARCH_TITLE%" -d "%DATABASE%" -u "%USER%" -p "%PASSWORD%" -f "%UPPER_DATE%"

REM Pause to keep the console open after the execution
pause

exit /b

REM Method to show the command help
:show_help
echo. 
echo Description: This program runs on the console, was developed in Python and uses a StackExchange API
echo to retrieve stackoverflow problems based on user-supplied search criteria, as of 01/14/2014. It then stores the results
echo in a PostgreSQL database, thanks to a Windows batch file (executable) that requests the necessary 
echo arguments to run the program.
echo.
echo Usage: %~nx0 -k "API Key" -i "Search Title" -d "Database name" -u "Database username" -p "Database user password" -f "Upper date (DD-MM-YYYY)" [-r]
echo.
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

:request_arguments
REM Request arguments one by one
set /p API_KEY="API Key: "
set /p SEARCH_TITLE="Search Title: "
set /p DATABASE="Database name: "
set /p USER="Database username: "
set /p PASSWORD="Database user password: "
set /p UPPER_DATE="Upper date (DD-MM-YYYY): "
goto run_script