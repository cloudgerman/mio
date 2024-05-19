import pathlib
import re
import subprocess
from typing import Generator

from mio import ext
from mio.cli_imap import _imap


def test_imap_command() -> None:

    class TestRclone(ext.Rclone):
        commands: list[str] = [
            "/usr/bin/rclone lsd 'remote:'",
            "/usr/bin/rclone mkdir 'remote:backups'",
            "/usr/bin/rclone copy /tmp/{PATH}/test@testable.com-{TIMESTAMP}.tgz remote:backups",
        ]

        def _run(
            self,
            cmd: str,
            capture_output: bool = True,
            env: dict[str, str] | None = None,
        ) -> subprocess.CompletedProcess[str]:
            expected_cmd = self.commands.pop(0)
            if " copy " in expected_cmd:
                cmd = re.sub(
                    r"\d{4}-\d{2}-\d{2}\.\d{2}-\d{2}-\d{2}", "{TIMESTAMP}", cmd
                )
                cmd = re.sub(r"/tmp/\w+/", "/tmp/{PATH}/", cmd)
            assert cmd == expected_cmd, f"'{cmd}' != '{expected_cmd}'"

            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="")

        def _runiter(
            self,
            cmd: str,
            env: dict[str, str] | None = None,
        ) -> Generator[str, None, None]:
            assert False

    class TestOfflineIMAP(ext.OfflineIMAP):
        commands: list[str] = []

        def _create_rc(
            self,
            imap_host: str,
            email: str,
            maildir: pathlib.Path,
        ) -> pathlib.Path:
            rc = super()._create_rc(imap_host, email, maildir)
            self.commands.append(f"/usr/bin/offlineimap  -c {rc} -a IMAP-Account")
            return rc

        def _run(
            self,
            cmd: str,
            capture_output: bool = True,
            env: dict[str, str] | None = None,
        ) -> subprocess.CompletedProcess[str]:
            assert False

        def _runiter(
            self,
            cmd: str,
            env: dict[str, str] | None = None,
        ) -> Generator[str, None, None]:
            expected_cmd = self.commands.pop(0)
            assert cmd == expected_cmd, f"'{cmd}' != '{expected_cmd}'"

            self._maildir().touch()
            self._logfile().touch()

            yield ""

    _imap(
        "test@testable.com",
        "remote:backups",
        "imap.testable.com",
        False,
        Rclone=TestRclone,
        OfflineIMAP=TestOfflineIMAP,
    )

    assert not TestOfflineIMAP.commands
    assert not TestRclone.commands
