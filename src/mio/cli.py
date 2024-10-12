import argparse

from . import _error
from .cloudflare import cloudflare
from .imap import imap


def main() -> None:
    ap = argparse.ArgumentParser(
        prog="mio",
        description="my backups",
    )
    sp = ap.add_subparsers(required=True)

    imap_sp = sp.add_parser("imap", help="imap backups")
    imap_sp.add_argument("email")
    imap_sp.add_argument("dst")
    imap_sp.add_argument("--imap-host", default="")
    imap_sp.add_argument("-d", "--debug", default=False)
    imap_sp.set_defaults(func=imap)

    cloudflare_sp = sp.add_parser("cloudflare", help="cloudflare backups")
    cloudflare_sp.add_argument("email")
    cloudflare_sp.add_argument("dst")
    cloudflare_sp.set_defaults(func=cloudflare)
    ns = ap.parse_args()

    try:
        if ns.func == imap:
            imap(ns.email, ns.dst, imap_host=ns.imap_host, debug=ns.debug)
        else:
            assert ns.func == cloudflare
            cloudflare(ns.email, ns.dst)
    except _error.MioError as e:
        print(e)
        exit(e.exit_code)
