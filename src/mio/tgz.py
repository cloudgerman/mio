import pathlib
import tarfile

import click


def pkg(workdir: pathlib.Path, stem: str, paths: list[pathlib.Path]) -> pathlib.Path:
    click.echo("[tgz] packing files: ", nl=False)

    tgz = workdir / f"{stem}.tgz"
    with tarfile.open(tgz, "w:gz") as tar:
        for path in paths:
            tar.add(path, arcname=path.name)

    click.echo("OK", nl=True)
    return tgz
