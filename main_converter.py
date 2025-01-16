from app import mideo_converter
from pathlib import Path


def main() -> None:
    target_path: Path = Path(r"I:\data\94f827b4b94e")
    merge_task_info: mideo_converter.types.MideoMergerTask = {
        "folder_path": target_path,
        "start_hour": 6,
        "delete_after": True,
    }
    mideo_converter.merger_handler(**merge_task_info, valid_extensions={".mp4"})

    cut_sl_speedup_task_info: mideo_converter.types.CutSlSpeedupTask = {
        "folder_path": target_path,
        "multiple": 0,
        "cut_sl_config": {"dB": -21},
    }
    mideo_converter.cut_sl_speedup_handler(**(cut_sl_speedup_task_info))


if __name__ == "__main__":
    main()
