ffmpeg -i 20241117_cut.mp4 -filter_complex "[0:v]setpts=0.01*PTS[v]                           ;[0:a]atempo=100[a]                            " -map "[v]" -map "[a]" output.mkv

ffmpeg -i 20241117_cut.mp4 -filter_complex "[0:v]setpts=PTS/(if(gte(mod(N\,2382)\,40)\,100\,1))[v];[0:a]atempo=(if(gte(mod(N\,2382)\,40)\,100\,1))[a]" -map "[v]" -map "[a]" output.mkv
ffmpeg -i 20241117_cut.mp4 -filter_complex "[0:v]setpts=PTS/(if(gte(mod(N\,2382)\,40)\,100\,1))[v]" -an -map "[v]" output.mkv
ffmpeg -i 20241117_cut.mp4 -filter_complex "[0:v]setpts=PTS*if(gte(mod(N\,2382)\,40)\,0.01\,1)[v]" -an -map "[v]" output.mkv

ffmpeg -i 20241117_cut.mp4 -filter_complex "[0:v]setpts=if(gte(mod(N\,2382)\,40)\,0.01\,1)*PTS[v]" -map "[v]" -an output.mkv

ffmpeg -i 20241117_cut.mp4 -vf "setpts=0.01*PTS" -af "atempo=100" output.mkv

ffmpeg -i 20241117_cut.mp4 -vf "setpts='if(gte(mod(N,2382),40),0.01*PTS,PTS)'" -an output.mkv
asetpts='if(lt(N,10),PTS+3/TB,PTS)'

ffmpeg -i 20241117_cut.mp4 -filter_complex "
[0:v]setpts=if(gte(mod(n,2382),40),0.01*PTS[v],PTS[v]):if(gte(t,10),-h,-h)
" output.mp4

ffmpeg -i 20241117_cut.mp4 -vf "select='if(lte(mod(n,2382),39.7),1,not(mod(n,99.25)))',setpts=N/FRAME_RATE/TB" -af "aselect='if(lte(mod(n,2382),39.7),1,not(mod(n,99.25)))',asetpts=N/SR/TB" -shortest -vsync vfr output.mkv

ffmpeg -i input.mkv -filter_complex "[0:v]setpts=0.5*PTS[v];[0:a]atempo=2[a]" -map "[v]" -map "[a]" output.mkv

ffmpeg -i input.mkv -ss 00:00:33 -to 00:01:00 -c:v copy -c:a copy output.mkv


ffmpeg -i 20241117_cut.mkv -f image2pipe -r 0.2 - | ffmpeg -i - -y out.mkv


ffmpeg -i 20241117_cut.mkv -filter:v "setpts=PTS/60" output.mkv


ffmpeg -i 20241117_cut.mkv -vf "select='gte(mod(n,99),77)',setpts=N/FRAME_RATE/TB" -af "aselect='gte(mod(n,99),77)',asetpts=N/SR/TB" -shortest -vsync vfr output.mkv


ffmpeg -i 20241117_cut.mp4 -filter_complex "[0:v]select='gte(mod(n,99),77)',setpts=0.01*PTS[v];[0:a]aselect='gte(mod(n,99),77)',atempo=100[a]" -map "[v]" -map "[a]" output.mkv



ffprobe -i 20241117_cut.mp4

ffmpeg -i 20241117_cut.mp4 -filter:v "fps=20" -c:v libx264  -preset fast -crf 23 -c:a copy output.mp4

ffmpeg -i 20241117_cut.mp4 -vf "
select='if(lte(mod(n,18.95*180),18.95*3),1,not(mod(n,18.95*5)))',setpts=N/FRAME_RATE/TB
" -af "
aselect='if(lte(mod(n,44100*180),44100*3),1,not(mod(n,44100*5)))',asetpts=N/SR/TB
" output.mkv

ffmpeg -i 20241117_cut.mp4 -vf "
select='if(lte(mod(t,180),3),1,not(mod(n,100)))',setpts=N/FRAME_RATE/TB
" -af "
aselect='if(lte(mod(t,180),3),1,not(mod(n,100)))',asetpts=N/SR/TB
" -shortest output.mkv

