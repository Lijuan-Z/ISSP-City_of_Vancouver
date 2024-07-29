@REM npm run build --prefix frontend
rmdir backend\static /Q /S
mkdir backend\static
xcopy frontend\out\_next\static\*.* backend\static /E
xcopy frontend\out\*.html backend\templates /Y
xcopy frontend\out\*.ico backend\templates /Y
xcopy frontend\out\*.ico backend\static /Y
xcopy frontend\out\*.svg backend\static /Y
xcopy frontend\out\*.png backend\static /Y
xcopy user_manual.pdf backend\static
python generate_frontend.py