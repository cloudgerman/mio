import argparse

from . import error
from .imap import imap


def main() -> None:
    ap = argparse.ArgumentParser(
        prog="mio",
        description="my backups",
    )
    sp = ap.add_subparsers()
    imap_sp = sp.add_parser("imap", help="imap backups")
    imap_sp.add_argument("email")
    imap_sp.add_argument("dst")
    imap_sp.add_argument("--imap-host", default="")
    imap_sp.add_argument("-d", "--debug", default=False)

    ns = ap.parse_args()

    try:
        imap(ns.email, ns.dst, imap_host=ns.imap_host, debug=ns.debug)
    except error.MioError as e:
        print(e)
        exit(e.exit_code)
