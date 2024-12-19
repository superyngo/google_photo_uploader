from app import mideo_converter
from app import config
from app.models.tasks import MideoMergerTask, SpeedupTask
from pathlib import Path


def main() -> None:
    target_path: Path = Path(r"H:\data\94f827b4b94e")
    merge_task_info: MideoMergerTask = {
        "folder_path": target_path,
        "start_hour": 6,
        "delete_after": True,
    }
    mideo_converter.merger_handler(**merge_task_info)

    speedup_task_info: SpeedupTask = {"folder_path": target_path, "multiple": 50}
    mideo_converter.speedup_handler(**speedup_task_info)


if __name__ == "__main__":
    main()
