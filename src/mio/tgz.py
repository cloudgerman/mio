import tarfile
from pathlib import Path


def pkg(workdir: Path, stem: str, paths: list[Path]) -> Path:
    print("[tgz] packing files: ", end="")

    tgz = workdir / f"{stem}.tgz"
    with tarfile.open(tgz, "w:gz") as tar:
        for path in paths:
            tar.add(path, arcname=path.name)

    print("OK")
    return tgz
