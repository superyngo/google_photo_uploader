from app import mideo_converter
from app import config
from app.models.tasks import MideoMergerTask, CutSlSpeedupTask
from pathlib import Path


def main() -> None:
    target_path: Path = Path(r"G:\data\94f827b4b94e")
    merge_task_info: MideoMergerTask = {
        "folder_path": target_path,
        "start_hour": 6,
        "delete_after": True,
    }
    mideo_converter.merger_handler(**merge_task_info)

    cut_sl_speedup_task_info: CutSlSpeedupTask = {
        "folder_path": target_path,
        "multiple": 0,
        "same_encode": False,
    }
    mideo_converter.cut_sl_speedup_handler(**(cut_sl_speedup_task_info))


if __name__ == "__main__":
    main()
