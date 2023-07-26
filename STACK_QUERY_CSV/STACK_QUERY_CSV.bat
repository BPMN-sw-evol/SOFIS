@echo off

REM Check if the help argument is provided
if /i "%~1"=="-h" goto show_help

REM Check if -r argument is provided to request arguments one by one
if /i "%~1"=="-r" goto request_arguments

REM Check if all required arguments are provided
if "%~5"=="" (
    echo Error: Insufficient arguments. Please provide all required parameters. For more information use [-h]
    echo Usage: %~nx0 -k "API Key" -i "Search Title" -u "Upper date (DD-MM-YYYY)" -d "Directory to save CSV files"
    exit /b 1
)

REM Parse the command line arguments
set "API_KEY="
set "SEARCH_TITLE="
set "UPPER_DATE="
set "DIRECTORY="

:parse_args
if "%~1"=="" (
    goto run_script
) else if /i "%~1"=="-k" (
    set "API_KEY=%~2"
    shift
) else if /i "%~1"=="-i" (
    set "SEARCH_TITLE=%~2"
    shift
) else if /i "%~1"=="-u" (
    set "UPPER_DATE=%~2"
    shift
) else if /i "%~1"=="-d" (
    set "DIRECTORY=%~2"
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

if "%UPPER_DATE%"=="" (
    echo Error: Upper date not provided. Use -u argument with a date in format DD-MM-YYYY. Example -u "12-06-2023".
    exit /b 1
)

if "%DIRECTORY%"=="" (
    echo Error: Directory not provided. Use -d argument with a directory. Example -d "/path/"
    exit /b 1
)

REM Code to execute the script with the provided arguments
python STACK_QUERY_CSV.py -k "%API_KEY%" -i "%SEARCH_TITLE%" -u "%UPPER_DATE%" -d "%DIRECTORY%"

REM Pause to keep the console open after the execution
pause

exit /b

:show_help
echo.
echo This program fetches Stackoverflow issues related to a specific BPM engine required by
echo user-supplied search criteria. They are obtained as of 14/01/2014 ( the official publication
echo date of the BPMN 2.0 standard). Stores the results in a CSV file provided by the user.
echo More info at https://github.com/BPMN-sw-evol/BPM_PC_S 
echo.
echo sage: %~nx0 -k "API Key" -i "Search Title" -u "Upper date (DD-MM-YYYY)" -d "Directory to save CSV files"
echo.
echo OPTIONS:
echo   -k, --key            StackExchange API Key (required)
echo                         Example: -k "ahhBNdmxDJ5zP2dxaJvCHw(("
echo.
echo   -i, --intitle        StackOverflow Search Title (required)
echo                         Example: -i "camunda"
echo.
echo   -u, --upper-date     Upper date to filter discussions (DD-MM-YYYY) (required)
echo                         Example: -s "12-06-2023"
echo.
echo   -d, --directory      Directory to save CSV files (required)
echo                         Example: -d "G:\Monitorias"
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
set /p UPPER_DATE="Upper date (DD-MM-YYYY): "
set /p DIRECTORY="Directory to save CSV files: "
goto run_script