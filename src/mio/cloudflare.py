import json
import tempfile

from datetime import datetime
from getpass import getpass
from pathlib import Path

from . import _ext
from ._serialize import serialize, SList, SType


def cloudflare(email: str, dst: str) -> None:
    api_key = getpass(prompt="Provide Cloudflare API Key: ")
    jdata = _cf_data(email, api_key)

    rclone = _ext.Rclone()
    remote, rpath = rclone.parse_dst(dst)

    rclone.guard_configured(remote)
    rclone.mkdir(remote, rpath)

    with tempfile.TemporaryDirectory() as dirname:
        tmpdir = Path(dirname)
        timestamp = datetime.now().strftime("%Y-%m-%d.%H-%M-%S")
        jsonfile = tmpdir / f"cloudflare-{timestamp}.json"

        with open(jsonfile, "w") as f:
            txt = json.dumps(jdata)
            print(txt, file=f)

        rclone.upload(jsonfile, remote, rpath)


def _cf_data(email: str, api_key: str) -> SType:
    # this import takes ages
    from cloudflare import Cloudflare

    client = Cloudflare(api_email=email, api_key=api_key)
    for zone in sorted(client.zones.list(), key=lambda x: x.id):
        print(f"[cloudflare] downloading {zone.name}: OK")
        jzone = serialize(zone)
        records: SList = []
        for dns in client.dns.records.list(zone_id=zone.id):
            print(f"[cloudflare] downloading dns record {dns.name}[{dns.type}]: OK")
            records.append(serialize(dns))
        assert isinstance(jzone, dict)
        assert "records" not in jzone
        jzone["records"] = records
    return jzone
