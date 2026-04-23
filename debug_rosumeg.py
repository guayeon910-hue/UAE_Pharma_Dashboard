import asyncio
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from frontend.server import _run_pipeline_for_product, _pipeline_tasks

logging.basicConfig(level=logging.DEBUG)

async def test():
    try:
        print("Starting pipeline for UAE_rosumeg_combigel")
        _pipeline_tasks["UAE_rosumeg_combigel"] = {
            "status": "running", "step": "init", "step_label": "시작 중…",
            "result": None, "refs": [], "pdf": None,
        }
        await _run_pipeline_for_product("UAE_rosumeg_combigel")
        print("Pipeline finished")
    except Exception as e:
        print(f"Pipeline crashed: {e}")
        import traceback
        traceback.print_exc()

asyncio.run(test())
