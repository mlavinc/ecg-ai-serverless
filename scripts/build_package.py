"""Build the AWS Lambda deployment artifact (``package/``) from ``backend/``.

What it does:
    1. Wipes ``package/``.
    2. Installs the Lambda dependencies as **Linux x86_64 / cp311** wheels
       (so the artifact works on Lambda even when built on Windows/Mac).
    3. Copies the runtime source modules from ``backend/`` into the flat
       ``package/`` root, rewriting imports from the local style
       (``from backend.services.model_loader import get_model``) to the
       Lambda style (``from model_loader import get_model``).
    4. Strips what Lambda already provides or does not need:
       boto3, botocore, *.dist-info, *.egg-info, __pycache__, tests.
    5. Bundles the synthetic test record into ``package/data/`` so the demo
       invocation (record_path="data/mock") works on AWS, where the function
       root /var/task is the working directory.
    6. Zips ``package/`` into ``lambda.zip`` with forward-slash paths (correct
       for AWS Lambda / Linux, unlike PowerShell 5.1's Compress-Archive).

Usage:
    python scripts/build_package.py      # produces package/ AND lambda.zip

Target runtime / wheel platform
-------------------------------
The default targets the **python3.11** Lambda runtime (Amazon Linux 2,
glibc 2.26) using ``manylinux2014`` (== manylinux_2_17) or older wheels, which
matches the pinned lightweight stack (numpy 1.26 / scipy 1.13 / scikit-learn
1.7 / joblib).

Override with env vars to target a newer runtime (e.g. python3.12 on Amazon
Linux 2023, which can also use manylinux_2_28 wheels):
    LAMBDA_PYTHON_VERSION=3.12 LAMBDA_PLATFORM=manylinux_2_28_x86_64 \
        python scripts/build_package.py
"""

import os
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
PACKAGE_DIR = PROJECT_ROOT / "package"
ZIP_PATH = PROJECT_ROOT / "lambda.zip"
REQUIREMENTS = PROJECT_ROOT / "requirements-lambda.txt"

# Target Lambda runtime (override via environment variables).
# Defaults target the python3.11 runtime (Amazon Linux 2, glibc 2.26), which
# requires manylinux2014 (== manylinux_2_17) or older wheels.
PYTHON_VERSION = os.environ.get("LAMBDA_PYTHON_VERSION", "3.11")

# pip's --platform matches a tag exactly (no implied backward compatibility),
# so we pass several compatible tags (all glibc <= 2.17, runnable on AL2).
_DEFAULT_PLATFORMS = [
    "manylinux_2_17_x86_64",
    "manylinux2014_x86_64",
    "manylinux2010_x86_64",
    "manylinux1_x86_64",
]
PLATFORMS = [
    p.strip()
    for p in os.environ.get("LAMBDA_PLATFORM", ",".join(_DEFAULT_PLATFORMS)).split(",")
    if p.strip()
]

# Runtime source modules to flatten into package/ root.
# (backend relative path -> flat file name)
SOURCE_MODULES = {
    "services/lambda_handler.py": "lambda_handler.py",
    "services/model_loader.py": "model_loader.py",
    "services/ecg_service.py": "ecg_service.py",
    "models/predict.py": "predict.py",
    "features/ecg_features.py": "ecg_features.py",
    "constants.py": "constants.py",
}

# Synthetic test record bundled into package/data/ so the demo invocation
# (record_path="data/mock") works on AWS without any file outside the ZIP.
TEST_DATA_FILES = ["mock.hea", "mock.dat"]

# Things Lambda already provides or that bloat the artifact.
PRUNE_TOP_LEVEL = {"boto3", "botocore", "pip", "setuptools", "wheel", "_distutils_hack"}
PRUNE_DIR_NAMES = {"__pycache__", "tests"}
PRUNE_DIR_SUFFIXES = (".dist-info", ".egg-info")

# Rewrites `from backend[.a.b].module import ...` -> `from module import ...`
IMPORT_RE = re.compile(r"\bfrom\s+backend(?:\.\w+)*\.(\w+)\s+import\b")


def wipe_package():
    if PACKAGE_DIR.exists():
        shutil.rmtree(PACKAGE_DIR)
    PACKAGE_DIR.mkdir(parents=True)


def install_dependencies():
    print(
        f"Installing Lambda deps (cp{PYTHON_VERSION}, "
        f"platforms: {', '.join(PLATFORMS)}) ..."
    )
    cmd = [
        sys.executable, "-m", "pip", "install",
        "-r", str(REQUIREMENTS),
        "--target", str(PACKAGE_DIR),
        "--python-version", PYTHON_VERSION,
        "--implementation", "cp",
        "--only-binary=:all:",
        "--upgrade",
    ]
    for platform in PLATFORMS:
        cmd.extend(["--platform", platform])
    subprocess.run(cmd, check=True)


def copy_sources():
    print("Copying and rewriting source modules ...")
    for rel_path, flat_name in SOURCE_MODULES.items():
        src = BACKEND_DIR / rel_path
        dst = PACKAGE_DIR / flat_name
        text = src.read_text(encoding="utf-8")
        rewritten = IMPORT_RE.sub(r"from \1 import", text)
        dst.write_text(rewritten, encoding="utf-8")
        print(f"  {rel_path} -> package/{flat_name}")


def copy_test_data():
    """Bundle the synthetic ECG record so record_path="data/mock" works on AWS.

    On AWS Lambda the function code root (/var/task) is the working directory,
    so a record at package/data/mock.{hea,dat} resolves from the relative path
    "data/mock" with no dependency on any local file outside the ZIP.
    """
    print("Bundling test ECG record (data/mock) ...")

    # Ensure the record exists (generate it from the source tree if missing).
    sys.path.insert(0, str(PROJECT_ROOT))
    from backend.utils.mock_ecg import ensure_mock_record

    src_base = PROJECT_ROOT / "data" / "mock"
    ensure_mock_record(str(src_base))

    dst_dir = PACKAGE_DIR / "data"
    dst_dir.mkdir(parents=True, exist_ok=True)
    for name in TEST_DATA_FILES:
        src = PROJECT_ROOT / "data" / name
        shutil.copy2(src, dst_dir / name)
        print(f"  data/{name} -> package/data/{name}")


def prune():
    print("Pruning unneeded files ...")
    # Remove top-level packages Lambda provides / we don't need.
    for name in PRUNE_TOP_LEVEL:
        target = PACKAGE_DIR / name
        if target.is_dir():
            shutil.rmtree(target)

    # Remove dist-info / egg-info / __pycache__ / tests recursively.
    for path in sorted(PACKAGE_DIR.rglob("*"), reverse=True):
        if not path.is_dir():
            continue
        if path.name in PRUNE_DIR_NAMES or path.name.endswith(PRUNE_DIR_SUFFIXES):
            shutil.rmtree(path, ignore_errors=True)

    # Remove stray .pyc files.
    for pyc in PACKAGE_DIR.rglob("*.pyc"):
        pyc.unlink(missing_ok=True)


def create_zip():
    """Zip package/ into lambda.zip using POSIX (forward-slash) arcnames.

    This is done in Python on purpose: Windows PowerShell 5.1's
    Compress-Archive writes backslash separators, which AWS Lambda (Linux)
    treats as literal filenames -- breaking both the bundled data file and
    every vendored package. as_posix() guarantees Lambda-correct paths.
    """
    print("Creating lambda.zip (forward-slash paths for Linux/Lambda) ...")
    if ZIP_PATH.exists():
        ZIP_PATH.unlink()
    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(PACKAGE_DIR.rglob("*")):
            if path.is_file():
                arcname = path.relative_to(PACKAGE_DIR).as_posix()
                zf.write(path, arcname)


def summary():
    total = sum(
        f.stat().st_size for f in PACKAGE_DIR.rglob("*") if f.is_file()
    )
    zip_mb = ZIP_PATH.stat().st_size / (1024 * 1024) if ZIP_PATH.exists() else 0
    print("\nBuild complete.")
    print(f"  package/ size : {total / (1024 * 1024):.1f} MB (unzipped)")
    print(f"  lambda.zip    : {zip_mb:.1f} MB")
    print("  Handler       : lambda_handler.lambda_handler")


def main():
    if not REQUIREMENTS.exists():
        sys.exit(f"Missing requirements file: {REQUIREMENTS}")
    wipe_package()
    install_dependencies()
    copy_sources()
    prune()
    copy_test_data()
    create_zip()
    summary()


if __name__ == "__main__":
    main()
