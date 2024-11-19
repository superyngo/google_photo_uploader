1:50:24
3:16:36

ffmpeg -i input.mkv -filter_complex "[0:v]setpts=0.5*PTS[v];[0:a]atempo=2[a]" -map "[v]" -map "[a]" output.mkv

ffmpeg -i input.mkv -ss 00:00:33 -to 00:01:00 -c:v copy -c:a copy output.mkv


ffmpeg -i 20241117_cut.mkv -f image2pipe -r 0.2 - | ffmpeg -i - -y out.mkv


ffmpeg -i 20241117_cut.mkv -filter:v "setpts=PTS/60" output.mkv


ffmpeg -i 20241117_cut.mkv -vf "select='gte(mod(n,99),77)',setpts=N/FRAME_RATE/TB" -af "aselect='gte(mod(n,99),77)',asetpts=N/SR/TB" -shortest -vsync vfr output.mkv


ffmpeg -i 20241117_cut.mp4 -filter_complex "[0:v]select='gte(mod(n,99),77)',setpts=0.01*PTS[v];[0:a]aselect='gte(mod(n,99),77)',atempo=100[a]" -map "[v]" -map "[a]" output.mkv



