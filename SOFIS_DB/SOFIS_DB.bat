@echo off

REM Check if the help argument is provided
if /i "%~1"=="-h" goto show_help

REM Check if -r argument is provided to request arguments one by one
if /i "%~1"=="-r" goto request_arguments

REM Check if all required arguments are provided
if "%~6"=="" (
    echo Error: Insufficient arguments. Please provide all required parameters. For more information use [-h]
    echo.
    echo Usage: %~nx0 -k "API Key" -i "Search Title" -d "Database name" -u "Database username" -p "Database user password" -f "Upper date (DD-MM-YYYY)"
    exit /b 1
)

REM Parse the command line arguments
set "API_KEY="
set "SEARCH_TITLE="
set "DATABASE="
set "USER="
set "PASSWORD="
set "UPPER_DATE="

:parse_args
if "%~1"=="" (
    goto run_script
) else if /i "%~1"=="-k" (
    set "API_KEY=%~2"
    shift
) else if /i "%~1"=="-i" (
    set "SEARCH_TITLE=%~2"
    shift
) else if /i "%~1"=="-d" (
    set "DATABASE=%~2"
    shift
) else if /i "%~1"=="-u" (
    set "USER=%~2"
    shift
) else if /i "%~1"=="-p" (
    set "PASSWORD=%~2"
    shift
) else if /i "%~1"=="-f" (
    set "UPPER_DATE=%~2"
    shift
) else (
    echo Unknown argument: %~1
    exit /b 1
)

shift
goto parse_args

:run_script
REM Check if all required arguments are provided
if "%API_KEY%"=="" (
    echo Error: API Key not provided. Use -k argument with a API_KEY. Example "ahhBNdmxDJ5zP2dxaJvCHw((".
    exit /b 1
)

if "%SEARCH_TITLE%"=="" (
    echo Error: Search Title not provided. Use -i argument with a title. Example -i "camunda".
    exit /b 1
)

if "%DATABASE%"=="" (
    echo Error: Database not provided. Use -d argument with a database. Example -d "SOFIS".
    exit /b 1
)

if "%USER%"=="" (
    echo Error: User not provided. Use -u argument with a user. Example -u "postgres"
    exit /b 1
)

if "%PASSWORD%"=="" (
    echo Error: password not provided. Use -p argument with a password. Example -p "1234"
    exit /b 1
)

if "%UPPER_DATE%"=="" (
    echo Error: Upper date not provided. Use -f argument with a date in format DD-MM-YYYY. Example -f "12-06-2023".
    exit /b 1
)

REM Code to execute the script with the provided arguments
python "SOFIS_DB.py" -k "%API_KEY%" -i "%SEARCH_TITLE%" -d "%DATABASE%" -u "%USER%" -p "%PASSWORD%" -f "%UPPER_DATE%"

REM Pause to keep the console open after the execution
pause

exit /b

:show_help
echo. 
echo This program fetches Stackoverflow issues related to a specific BPM engine required by
echo user-supplied search criteria. They are obtained as of 14/01/2014 ( the official publication
echo date of the BPMN 2.0 standard). Stores the results in a PostgreSQL database provided by the user.
echo More info at https://github.com/BPMN-sw-evol/SOFIS.git 
echo.
echo Usage: %~nx0 -k "API Key" -i "Search Title" -d "Database name" -u "Database username" -p "Database user password" -f "Upper date (DD-MM-YYYY)"
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
echo   -r                   Request arguments one by one
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
