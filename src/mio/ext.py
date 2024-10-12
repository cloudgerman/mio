import pathlib
import shutil
import subprocess
from typing import Generator

from . import error


class Command(object):
    def __init__(self, exe: str) -> None:
        fullpath = shutil.which(exe)
        if not fullpath:
            raise error.CommandNotFoundError(f"'{exe}' could not be found in the path")
        self.exe = pathlib.Path(fullpath)

    def _run(
        self,
        cmd: str,
        capture_output: bool = True,
        env: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        p = subprocess.run(
            cmd, capture_output=capture_output, env=env, text=True, shell=True
        )
        return p

    def _runiter(
        self,
        cmd: str,
        env: dict[str, str] | None = None,
    ) -> Generator[str, None, None]:
        with subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=env,
            text=True,
            shell=True,
        ) as p:
            if p.stdout:
                for line in p.stdout:
                    yield line
            p.wait()
            if p.returncode:
                raise error.CommandError(f"'{cmd}' failed with error: {p.returncode}")


class Rclone(Command):
    def __init__(self) -> None:
        super().__init__(exe="rclone")

    def parse_dst(self, dst: str) -> tuple[str, pathlib.Path]:
        sep = ":"
        if sep not in dst:
            raise error.ArgParsingError(
                f"'{dst}' must conform to the pattern 'remote:path'"
            )
        remote, path = dst.split(sep, maxsplit=1)
        return (remote, pathlib.Path(path))

    def guard_configured(self, remote: str) -> None:
        print("[rclone] testing configuration: ", end="")

        cmd = f"{self.exe!s} lsd '{remote}:'"
        p = self._run(cmd)
        if p.returncode:
            print("ERROR")
            raise error.GuardError(f"'{cmd}' failed with error: {p.stdout}")

        print("OK")

    def mkdir(self, remote: str, path: pathlib.Path) -> None:
        print("[rclone] creating path {remote}:{path!s}: ", end="")

        cmd = f"{self.exe!s} mkdir '{remote}:{path!s}'"
        p = self._run(cmd)
        if p.returncode:
            print("ERROR")
            raise error.CommandError(f"'{cmd}' failed with error: {p.stdout}")

        print("OK")

    def upload(self, file: pathlib.Path, remote: str, path: pathlib.Path) -> None:
        print("[rclone] upload: ", end="")

        cmd = f"{self.exe!s} copy {file!s} {remote}:{path!s}"
        p = self._run(cmd)
        if p.returncode:
            print("ERROR")
            raise error.CommandError(f"'{cmd}' failed with error: {p.stdout}")

        print("OK")


class OfflineIMAP(Command):
    def __init__(self, workdir: pathlib.Path, debug: bool = False) -> None:
        super().__init__(exe="offlineimap")
        self._workdir = workdir
        self._debug = debug

    def _envvars(self) -> dict[str, str]:
        return {"XDG_CONFIG_HOME": str(self._workdir)}

    def _create_rc(
        self,
        imap_host: str,
        email: str,
        maildir: pathlib.Path,
    ) -> pathlib.Path:
        rcpath = self._workdir / ".offlineimaprc"
        with open(rcpath, "w") as f:
            cfg = self._cfg(imap_host, email, maildir)
            f.write(cfg)
        return rcpath

    def _maildir(self) -> pathlib.Path:
        return self._workdir / "maildir"

    def _logfile(self) -> pathlib.Path:
        return self._workdir / "download.log"

    def download(self, imap_host: str, email: str) -> list[pathlib.Path]:
        print("[offlineimap] starting download")

        maildir = self._maildir()
        log = self._logfile()

        rcpath = self._create_rc(imap_host, email, maildir)

        debug = (self._debug and "-d imap") or ""
        cmd = f"{self.exe!s} {debug} -c {rcpath!s} -a IMAP-Account"
        with open(log, "w") as flog:
            for line in self._runiter(cmd, env=self._envvars()):
                print(line, end="")
                print(line, end="", file=flog)

        print("[offlineimap] download complete")
        return [maildir, log]

    def _cfg(self, imap_host: str, email: str, maildir: pathlib.Path) -> str:
        # this is ugly but quite simple. maybe adding templating later
        return f"""[general]
maxsyncaccounts = 1
ui = TTYUI
socktimeout = 120
retrycount = 10
accounts = IMAP-Account

[Account IMAP-Account]
localrepository = MAILDIR
remoterepository = IMAP-Remote
quick=-1

[Repository MAILDIR]
type = Maildir
localfolders = {maildir!s}
sep = /

[Repository IMAP-Remote]
type = IMAP
sslcacertfile = /etc/ssl/certs/ca-certificates.crt
remotehost = {imap_host}
remoteuser = {email}
"""
