import os
import sys

REQUIRED_ENV = "speciesnet"

current = os.environ.get("CONDA_DEFAULT_ENV") or os.environ.get("VIRTUAL_ENV")
if current is None:
    sys.stderr.write("[ENV GUARD] 未检测到Conda或虚拟环境，请先执行: conda activate speciesnet\n")
    sys.exit(1)

if current.endswith("/speciesnet") or current.endswith("\\speciesnet"):
    # VIRTUAL_ENV path case
    pass
elif current != REQUIRED_ENV:
    sys.stderr.write(f"[ENV GUARD] 当前环境 '{current}' != '{REQUIRED_ENV}'\n")
    sys.stderr.write("请执行: conda activate speciesnet\n")
    sys.exit(2)

# Optional: also verify python executable path contains env name
py_exec = sys.executable.lower()
if REQUIRED_ENV not in py_exec:
    sys.stderr.write(f"[ENV GUARD] Python可执行路径未包含 {REQUIRED_ENV}: {py_exec}\n")
    sys.stderr.write("可能未正确激活环境，请重新激活。\n")
    sys.exit(3)

# If reached here, it's fine
if __name__ == "__main__":
    print(f"[ENV GUARD] OK - 当前环境: {current}")
