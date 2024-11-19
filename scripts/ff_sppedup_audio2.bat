@echo off


REM Set the interval 
set "fps=19.85"
set "interval=150"
set "lasting=1"


REM Precompute FFmpeg expressions
set "frame_select_expr=gte(mod(n,%fps%*%interval%),%fps%*(%interval%-%lasting%))"

REM Check if files were dragged and dropped
if "%~1"=="" (
    echo No files dragged. Processing all MKV files in the current folder.
    for %%F in (*.mkv) do (
        echo Processing: %%F
        ffmpeg -i "%%F" -vf "select='%frame_select_expr%',setpts=N/FRAME_RATE/TB" -af "aselect='%frame_select_expr%',asetpts=N/SR/TB" -shortest -vsync vfr "%%~nF_speedup.mkv"
    )
) else (
    echo Files dragged. Processing pulled files.
    :process_args
    if "%~1"=="" goto :done
    echo Processing: %~1
    ffmpeg -i "%~1" -vf "select='%frame_select_expr%',setpts=N/FRAME_RATE/TB" -af "aselect='%frame_select_expr%',asetpts=N/SR/TB" -shortest -vsync vfr "%~n1_speedup.mkv"
    shift
    goto :process_args
)
:done

echo All processing done.
pause
