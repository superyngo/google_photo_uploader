1:50:24
3:16:36

ffmpeg -i input.mkv -ss 00:00:33 -to 00:01:00 -c:v copy -c:a copy output.mkv


ffmpeg -i 20241117_cut.mkv -f image2pipe -r 0.2 - | ffmpeg -i - -y out.mkv


ffmpeg -i 20241117_cut.mkv -filter:v "setpts=PTS/60" output.mkv


ffmpeg -i 20241117_cut.mkv -vf "select='not(mod(t,300))',setpts=N/FRAME_RATE/TB" -af "aselect='not(mod(t,300))',asetpts=N/SR/TB" -shortest output.mkv
ffmpeg -i 20241117_cut.mkv -vf "select='not(mod(n,150))',setpts=N/FRAME_RATE/TB" -vsync vfr output.mkv
ffmpeg -i 20241117_cut.mkv -vf "select='not(mod(n,99))',setpts=N/FRAME_RATE/TB" -vsync vfr output.mkv
ffmpeg -i 20241117_cut.mkv -vf "select='gte(mod(n,99),77)',setpts=N/FRAME_RATE/TB" -vsync vfr output.mkv
ffmpeg -i 20241117_cut.mkv -vf "select='gte(mod(n,99),77)',setpts=N/FRAME_RATE/TB" -af "aselect='gte(mod(n,99),77)',asetpts=N/SR/TB" -shortest -vsync vfr output.mkv






ffmpeg -i 20241117_cut.mkv -f segment -segment_time 5 output.mkv