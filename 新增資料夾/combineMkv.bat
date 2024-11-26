:: Create File List
for %%i in (*.mkv) do echo file '%%i'>> mylist.txt

:: Concatenate Files
ffmpeg -f concat -safe 0 -i mylist.txt -map 0 -c:v copy -c:a copy output.mkv
