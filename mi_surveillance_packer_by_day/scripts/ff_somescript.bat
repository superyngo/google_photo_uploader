@REM set speed 
ffmpeg -i 20241117_cut.mp4 -vf "setpts=0.01*PTS" -af "atempo=100" output.mkv
ffmpeg -i input.mkv -filter_complex "[0:v]setpts=0.5*PTS[v];[0:a]atempo=2[a]" -map "[v]" -map "[a]" output.mkv
ffmpeg -i 20241117_cut.mp4 -vf "setpts='if(gte(mod(N,2382),40),0.01*PTS,PTS)'" -an output.mkv
ffmpeg -i 20241117_cut.mkv -filter:v "setpts=PTS/60" output.mkv

@REM cut
ffmpeg -i input.mkv -ss 00:00:33 -to 00:01:00 -c:v copy -c:a copy output.mkv

@REM speedup by image
ffmpeg -i 20241117_cut.mkv -f image2pipe -r 0.2 - | ffmpeg -i - -an -y out.mkv

@REM jumpcut by t and speedup by n
ffmpeg -i 20241117_cut.mp4 -vf "
select='if(lte(mod(t,180),3),1,not(mod(n,100)))',setpts=N/FRAME_RATE/TB
" -af "
aselect='if(lte(mod(t,180),3),1,not(mod(n,100)))',asetpts=N/SR/TB
" -shortest output.mkv

@REM probe
ffprobe -i 20241117_cut.mp4

@REM set fps
ffmpeg -i 20241117_cut.mp4 -filter:v "fps=20" -c:v libx264  -preset fast -crf 23 -c:a copy output.mp4




