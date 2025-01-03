from app import mideo_converter
from app import config
from app.models.tasks import MideoMergerTask, CutSlSpeedupTask
from pathlib import Path


def main() -> None:
    target_path: Path = Path(
        r"D:\Users\user\OneDrive - Chunghwa Telecom Co., Ltd\文件\Projects\Python\sample"
    )
    merge_task_info: MideoMergerTask = {
        "folder_path": target_path,
        "start_hour": 6,
        "delete_after": True,
    }
    mideo_converter.merger_handler(**merge_task_info)

    cut_sl_speedup_task_info: CutSlSpeedupTask = {
        "folder_path": target_path,
        "multiple": 3,
        "same_encode": True,
    }
    mideo_converter.cut_sl_speedup_handler(
        **(cut_sl_speedup_task_info | {"valid_extensions": {".mp4"}})
    )


if __name__ == "__main__":
    main()

# interval=6
# lasting=1
# input_file=Path(r"C:\Users\user\Downloads\2024-12-19.mkv")
# output_file=r"C:\Users\user\Downloads\2024-12-19_speedup.mkv"

# ffmpeg_converter.probe_encoding_info(input_file)

# ffmpeg.input(input_file)
#             .output(
#                 str(output_file),
#                 vf=f"select='lte(mod(t,{interval}),{lasting})',setpts={1/speed}*PTS",
#                 af=f"aselect='lte(mod(t,{interval}),{lasting})',atempo={speed}",
#                 map=0,
#                 shortest=None,
#                 fps_mode="vfr",
#                 **othertags,
#             )
#             .run()
