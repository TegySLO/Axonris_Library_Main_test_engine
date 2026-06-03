@echo off
echo ========================================================
echo         Axonris Sub-Engine Installer
echo ========================================================
echo.
echo Ta namestitev bo vzpostavila tvojega lokalnega AI Asistenta (Sub-Engine)
echo in ga povezala z osrednjo bazo znanj (Main Engine).
echo.
echo Korak 1: Prenos zanesljivega okolja...
python -m venv venv_sub_engine
call venv_sub_engine\Scripts\activate

echo Korak 2: Namestitev orodij...
pip install openai requests colorama

echo Korak 3: Prenos zadnje baze znanj...
if not exist "Knowledge_Base" (
    git clone https://github.com/TegySLO/Axonris_Library_Main_test_engine.git Knowledge_Base
) else (
    cd Knowledge_Base
    git pull origin master
    cd ..
)

echo.
echo ========================================================
echo Namestitev ZAKLJUCENA!
echo ========================================================
echo Za zagon svojega lokalnega asistenta zazeni:
echo start_agent.bat
pause
