@echo off


REM Set the interval 
set "interval=60"
set "lasting=1"
set "postfix=jumpcut_speedup"
set "speed=100"


REM Precompute FFmpeg expressions
set "frame_select_expr='if(lte(mod(t,%interval%),%lasting%),1,not(mod(n,%speed%)))'"

REM Check if files were dragged and dropped
if "%~1"=="" (
    echo No files dragged. Processing all MKV files in the current folder.
    for %%F in (*.mkv) do (
        echo Processing: %%F
        ffmpeg -i "%%F" -vf "select=%frame_select_expr%,setpts=N/FRAME_RATE/TB" -af "aselect=%frame_select_expr%,asetpts=N/SR/TB" -shortest -vsync vfr "%%~nF_%postfix%.mkv"
    )
) else (
    echo Files dragged. Processing pulled files.
    :process_args
    if "%~1"=="" goto :done
    echo Processing: %~1
    ffmpeg -i "%~1" -vf "select=%frame_select_expr%,setpts=N/FRAME_RATE/TB" -af "aselect=%frame_select_expr%,asetpts=N/SR/TB" -shortest -vsync vfr "%~n1_%postfix%.mkv"
    shift
    goto :process_args
)
:done

echo All processing done.
pause