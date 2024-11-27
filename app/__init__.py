from .config.config import APP_NAME, CONFIG_PATH, APP_BASE_DIR, SESSIONS_DIR, HANDLE_SPEEDUP, BASE_PATH

# Create App directories if they don't exist
APP_BASE_DIR.mkdir(parents=True, exist_ok=True)
SESSIONS_DIR.mkdir(exist_ok=True)

__all__: list[str] = ['APP_NAME', 'APP_BASE_DIR', 'CONFIG_PATH', 'SESSIONS_DIR', 'HANDLE_SPEEDUP', 'BASE_PATH']
print(locals())