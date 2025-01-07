from app import mideo_converter
from app import config
from app.models.tasks import MideoMergerTask, CutSlSpeedupTask
from pathlib import Path


def main() -> None:
    target_path: Path = Path(
        r"D:\Users\user\OneDrive - Chunghwa Telecom Co., Ltd\文件\Projects\Python\sample\tt"
    )
    merge_task_info: MideoMergerTask = {
        "folder_path": target_path,
        "start_hour": 6,
        "delete_after": True,
    }
    mideo_converter.merger_handler(**merge_task_info)

    cut_sl_speedup_task_info: CutSlSpeedupTask = {
        "folder_path": target_path,
        "multiple": 2,
        "same_encode": False,
    }
    mideo_converter.cut_sl_speedup_handler(**(cut_sl_speedup_task_info))


if __name__ == "__main__":
    main()
