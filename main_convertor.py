from app import mideo_convertor
from app import config
from app.models.tasks import MideoMergerTask, CutSlSpeedupTask
from pathlib import Path


def main() -> None:
    target_path: Path = Path(
        r"D:\Users\user\OneDrive - Chunghwa Telecom Co., Ltd\文件\Projects\Python\sample\cut_sl_speedup"
    )
    merge_task_info: MideoMergerTask = {
        "folder_path": target_path,
        "start_hour": 6,
        "delete_after": True,
    }
    mideo_convertor.merger_handler(**merge_task_info, valid_extensions={".mp4"})

    cut_sl_speedup_task_info: CutSlSpeedupTask = {
        "folder_path": target_path,
        "multiple": 0,
        "cut_sl_config": {"dB": -21},
    }
    mideo_convertor.cut_sl_speedup_handler(**(cut_sl_speedup_task_info))


if __name__ == "__main__":
    main()
