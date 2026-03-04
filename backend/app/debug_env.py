"""
実行環境同一性確定用の一時エンドポイント（Phase 1 Step 1）。
原因確定後に削除または無効化すること。
"""
import os
import glob
from fastapi import APIRouter

router = APIRouter()


@router.get("/__debug_env")
def debug_env():
    def safe_listdir(p: str):
        if not os.path.exists(p):
            return "NOT_FOUND"
        try:
            return os.listdir(p)
        except Exception as e:
            return str(e)

    ipa_glob = []
    dejavu_glob = []
    try:
        ipa_glob = glob.glob("/usr/share/fonts/**/*ipa*", recursive=True)
        dejavu_glob = glob.glob("/usr/share/fonts/**/*DejaVu*", recursive=True)
    except Exception as e:
        ipa_glob = [f"glob_error: {e}"]
        dejavu_glob = [f"glob_error: {e}"]

    build_marker = "NOT_FOUND"
    if os.path.exists("/BUILD_MARKER"):
        try:
            with open("/BUILD_MARKER") as f:
                build_marker = f.read().strip()
        except Exception as e:
            build_marker = str(e)

    return {
        "cwd": os.getcwd(),
        "app_list": safe_listdir("/app"),
        "app_fonts_list": safe_listdir("/app/fonts"),
        "ipa_system_paths": ipa_glob,
        "dejavu_paths": dejavu_glob,
        "build_marker": build_marker,
        "RENDER_GIT_COMMIT": os.environ.get("RENDER_GIT_COMMIT"),
        "env_sample": dict(list(os.environ.items())[:20]),
    }
