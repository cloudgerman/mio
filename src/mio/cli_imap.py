import pathlib
import tempfile
from datetime import datetime
from typing import Type

import click

from . import error, ext, tgz


@click.command()
@click.argument("email")
@click.argument("dst")
@click.option("--imap-host", default="")
@click.option("-d", "--debug/--no-debug", default=False)
def imap(
    email: str,
    dst: str,
    imap_host: str,
    debug: bool,
) -> None:
    _imap(email, dst, imap_host, debug)


def _imap(
    email: str,
    dst: str,
    imap_host: str,
    debug: bool,
    # these are to easily test it
    Rclone: Type[ext.Rclone] = ext.Rclone,
    OfflineIMAP: Type[ext.OfflineIMAP] = ext.OfflineIMAP,
) -> None:
    """Backup an imap account"""
    if not imap_host:
        # TODO - include basic options for main email providers
        pass

    try:
        rclone = Rclone()
        remote, rpath = rclone.parse_dst(dst)

        rclone.guard_configured(remote)
        rclone.mkdir(remote, rpath)

        with tempfile.TemporaryDirectory() as dirname:
            tmpdir = pathlib.Path(dirname)
            oimap = OfflineIMAP(tmpdir, debug)
            paths = oimap.download(imap_host, email)

            timestamp = datetime.now().strftime("%Y-%m-%d.%H-%M-%S")
            zipped = tgz.pkg(tmpdir, f"{email}-{timestamp}", paths)

            rclone.upload(zipped, remote, rpath)
    except error.MioError as e:
        click.echo(e)
        exit(e.exit_code)
