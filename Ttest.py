import re
from app.services import ffmpeg_converter

log_data = """
ffmpeg version 2024-11-18-git-970d57988d-full_build-www.gyan.dev Copyright (c) 2000-2024 the FFmpeg developers
  built with gcc 14.2.0 (Rev1, Built by MSYS2 project)
  configuration: --enable-gpl --enable-version3 --enable-static --disable-w32threads --disable-autodetect --enable-fontconfig --enable-iconv --enable-gnutls --enable-libxml2 --enable-gmp --enable-bzlib --enable-lzma --enable-libsnappy --enable-zlib --enable-librist --enable-libsrt --enable-libssh --enable-libzmq --enable-avisynth --enable-libbluray --enable-libcaca --enable-sdl2 --enable-libaribb24 --enable-libaribcaption --enable-libdav1d --enable-libdavs2 --enable-libopenjpeg --enable-libquirc --enable-libuavs3d --enable-libxevd --enable-libzvbi --enable-libqrencode --enable-librav1e --enable-libsvtav1 --enable-libvvenc --enable-libwebp --enable-libx264 --enable-libx265 --enable-libxavs2 --enable-libxeve --enable-libxvid --enable-libaom --enable-libjxl --enable-libvpx --enable-mediafoundation --enable-libass --enable-frei0r --enable-libfreetype --enable-libfribidi --enable-libharfbuzz --enable-liblensfun --enable-libvidstab --enable-libvmaf --enable-libzimg --enable-amf --enable-cuda-llvm --enable-cuvid --enable-dxva2 --enable-d3d11va --enable-d3d12va --enable-ffnvcodec --enable-libvpl --enable-nvdec --enable-nvenc --enable-vaapi --enable-libshaderc --enable-vulkan --enable-libplacebo --enable-opencl --enable-libcdio --enable-libgme --enable-libmodplug --enable-libopenmpt --enable-libopencore-amrwb --enable-libmp3lame --enable-libshine --enable-libtheora --enable-libtwolame --enable-libvo-amrwbenc --enable-libcodec2 --enable-libilbc --enable-libgsm --enable-liblc3 --enable-libopencore-amrnb --enable-libopus --enable-libspeex --enable-libvorbis --enable-ladspa --enable-libbs2b --enable-libflite --enable-libmysofa --enable-librubberband --enable-libsoxr --enable-chromaprint
  libavutil      59. 47.100 / 59. 47.100
  libavcodec     61. 25.100 / 61. 25.100
  libavformat    61.  9.100 / 61.  9.100
  libavdevice    61.  4.100 / 61.  4.100
  libavfilter    10.  6.101 / 10.  6.101
  libswscale      8.  9.101 /  8.  9.101
  libswresample   5.  4.100 /  5.  4.100
  libpostproc    58.  4.100 / 58.  4.100
Input #0, mov,mp4,m4a,3gp,3g2,mj2, from 'output.mp4':
  Metadata:
    major_brand     : isom
    minor_version   : 512
    compatible_brands: isomiso2avc1mp41
    encoder         : Lavf61.9.100
  Duration: 00:44:00.04, start: 0.003991, bitrate: 1223 kb/s
  Stream #0:0[0x1](und): Video: h264 (High) (avc1 / 0x31637661), yuv420p(tv, bt709, progressive), 1920x1080 [SAR 1:1 DAR 16:9], 1124 kb/s, 19.85 fps, 19.85 tbr, 23806 tbn (default)
    Metadata:
      handler_name    : ISO Media file produced by Google Inc.
      vendor_id       : [0][0][0][0]
  Stream #0:1[0x2](und): Audio: aac (LC) (mp4a / 0x6134706D), 44100 Hz, mono, fltp, 95 kb/s (default)
    Metadata:
      handler_name    : ISO Media file produced by Google Inc.
      vendor_id       : [0][0][0][0]
Stream mapping:
  Stream #0:0 -> #0:0 (h264 (native) -> wrapped_avframe (native))
  Stream #0:1 -> #0:1 (aac (native) -> pcm_s16le (native))
Press [q] to stop, [?] for help
[silencedetect @ 000001aa30ce8a00] silence_start: 0
Output #0, null, to 'pipe:':
  Metadata:
    major_brand     : isom
    minor_version   : 512
    compatible_brands: isomiso2avc1mp41
    encoder         : Lavf61.9.100
  Stream #0:0(und): Video: wrapped_avframe, yuv420p(tv, bt709, progressive), 1920x1080 [SAR 1:1 DAR 16:9], q=2-31, 200 kb/s, 19.85 fps, 19.85 tbn (default)
    Metadata:
      encoder         : Lavc61.25.100 wrapped_avframe
      handler_name    : ISO Media file produced by Google Inc.
      vendor_id       : [0][0][0][0]
  Stream #0:1(und): Audio: pcm_s16le, 44100 Hz, mono, s16, 705 kb/s (default)
    Metadata:
      encoder         : Lavc61.25.100 pcm_s16le
      handler_name    : ISO Media file produced by Google Inc.
      vendor_id       : [0][0][0][0]
[silencedetect @ 000001aa30ce8a00] silence_end: 8.00517 | silence_duration: 8.00517
[silencedetect @ 000001aa30ce8a00] silence_start: 19.957483
[silencedetect @ 000001aa30ce8a00] silence_end: 25.096395 | silence_duration: 5.138912
[silencedetect @ 000001aa30ce8a00] silence_start: 25.21644
frame=  569 fps=0.0 q=-0.0 size=N/A time=00:00:30.57 bitrate=N/A speed=59.7x    
[silencedetect @ 000001aa30ce8a00] silence_end: 34.379161 | silence_duration: 9.162721
[silencedetect @ 000001aa30ce8a00] silence_start: 35.017052
[silencedetect @ 000001aa30ce8a00] silence_end: 41.201338 | silence_duration: 6.184286

[out#0/null @ 000001aa30cab840] video:22507KiB audio:227392KiB subtitle:0KiB other streams:0KiB global headers:0KiB muxing overhead: unknown
frame=52380 fps=879 q=-0.0 Lsize=N/A time=00:44:00.01 bitrate=N/A speed=44.3x
"""
# Regular expression to find all floats after "silence_end: "
pattern = r"silence_(?:start|end): (\d+\.\d+)"

# Find all matches in the log data
matches = re.findall(pattern, log_data)

# Convert matches to a list of floats
silence_end_floats = [float(match) for match in matches]

print(silence_end_floats)
