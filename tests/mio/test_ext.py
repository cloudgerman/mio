import pathlib
import subprocess
import tempfile
from typing import Generator

import pytest

from mio import error, ext


def test_exe() -> None:
    assert ext.Rclone().exe == pathlib.Path("/usr/bin/rclone")
    assert ext.OfflineIMAP(pathlib.Path("/tmp")).exe == pathlib.Path(
        "/usr/bin/offlineimap"
    )


def test_exe_fail() -> None:
    with pytest.raises(error.CommandNotFoundError):
        ext.Command("blablabla")


def test_command_run_error() -> None:
    c = ext.Command("false")
    p = c._run("false")
    assert p.returncode


def test_command_runiter_error() -> None:
    c = ext.Command("false")
    with pytest.raises(error.CommandError):
        list(c._runiter("echo abc ; false"))


def test_rclone_parse_dst() -> None:
    rclone = ext.Rclone()
    remote, path = rclone.parse_dst("remote:path")
    assert remote == "remote"
    assert path == pathlib.Path("path")


def test_rclone_parse_dst_error() -> None:
    rclone = ext.Rclone()
    with pytest.raises(error.ArgParsingError):
        rclone.parse_dst("remote_path")


def test_rclone_error() -> None:
    class TRclone(ext.Rclone):
        def _run(
            self,
            cmd: str,
            capture_output: bool = True,
            env: dict[str, str] | None = None,
        ) -> subprocess.CompletedProcess[str]:
            if cmd == "which rclone":
                return subprocess.CompletedProcess(
                    args=cmd, returncode=0, stdout="/usr/bin/rclone"
                )
            return subprocess.CompletedProcess(args=cmd, returncode=1)

    r = TRclone()
    with pytest.raises(error.GuardError):
        r.guard_configured("remote")
    with pytest.raises(error.CommandError):
        r.mkdir("remote", pathlib.Path("path"))
    with pytest.raises(error.CommandError):
        f = pathlib.Path(__file__)
        r.upload(f, "remote", pathlib.Path("path"))


def test_offlineimap_download_fail() -> None:
    class TOfflineIMAP(ext.OfflineIMAP):
        def _runiter(
            self,
            cmd: str,
            env: dict[str, str] | None = None,
        ) -> Generator[str, None, None]:
            raise error.CommandError(f"'{cmd}' failed with error: 1")

    with tempfile.TemporaryDirectory() as tmpdir:
        oimap = TOfflineIMAP(pathlib.Path(tmpdir))
        with pytest.raises(error.CommandError):
            oimap.download("imap.test.com", "test@testable.com")


def test_offlineimap_download() -> None:
    class TOfflineIMAP(ext.OfflineIMAP):
        def _runiter(
            self,
            cmd: str,
            env: dict[str, str] | None = None,
        ) -> Generator[str, None, None]:
            yield "test"

    with tempfile.TemporaryDirectory() as tmpdir:
        oimap = TOfflineIMAP(pathlib.Path(tmpdir))
        paths = oimap.download("imap.test.com", "test@testable.com")
        assert len(paths) == 2
        assert paths[0].name == "maildir"
        assert paths[1].name == "download.log"
