from __future__ import annotations

import os
import logging

from importlib.metadata import metadata
from pathlib import Path

# own imports
from depsight.utils.utils import discover_plugins, resolve_user_dir, resolve_output_dir

#
# APP
# # # # # # # #
APP_LICENSE: str = metadata("depsight")["License-Expression"]
APP_NAME: str = metadata("depsight")["Name"]
DEV_MODE: bool = os.getenv("DEPSIGHT_ENV", "production").lower() == "development"

#
# PLUGINS
# # # # # # # #
SUPPORTED_PLUGINS: dict = discover_plugins(APP_NAME)

#
# PATHS
# # # # # # # #
USER_HOME: Path = Path.home()
DEPSIGHT_HOME: Path = resolve_user_dir(APP_NAME, dev_mode=DEV_MODE)
USER_LOG_DIR: Path = DEPSIGHT_HOME / "logs"
USER_DATA_DIR: Path = resolve_output_dir(DEPSIGHT_HOME / "data")

#
# LOGGING
# # # # # # # #
LOG_DIR: str = f"{APP_NAME}./logs"
LOG_FORMAT: str = "[%(asctime)s][%(levelname)s][%(name)s][%(message)s]"
LOG_DATE_FORMAT: str = "%Y-%m-%d][%H:%M:%S"
LOG_MAX_BYTES: int = 5 * 1024 * 1024  # 5 MB per file
LOG_BACKUP_COUNT: int = 3
LOG_FILE_NAME: str = f"{APP_NAME}.log"
LOG_JSONL_FILE_NAME: str = f"{APP_NAME}.jsonl"
LOG_LEVEL: int = logging.INFO

#
# TUI
# # # # # # # #
COLOR_DIM_ORANGE: str = "#CD853F"      # peru
COLOR_PEACH: str = "#FFDAB9"           # peach-puff

APP_BANNER: str = f"""
[bold {COLOR_DIM_ORANGE}]  ____                 _       _     _
 |  _ \\  ___ _ __  ___(_) __ _| |__ | |_
 | | | |/ _ \\ '_ \\/ __| |/ _` | '_ \\| __|
 | |_| |  __/ |_) \\__ \\ | (_| | | | | |_
 |____/ \\___| .__/|___/_|\\__, |_| |_|\\__|
            |_|          |___/[/bold {COLOR_DIM_ORANGE}]
 [dim {COLOR_PEACH}]A modern dependency analysis CLI[/dim {COLOR_PEACH}]
"""