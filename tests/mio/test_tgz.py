import pathlib
import tarfile
import tempfile

from mio import _tgz


def test_tgz() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        workdir = pathlib.Path(tmpdir)
        file = workdir / "file.txt"
        file.touch()

        pkg = _tgz.pkg(workdir, "test", [file])
        with tarfile.open(pkg, "r|gz") as tar:
            assert tar.getnames() == [file.name]
