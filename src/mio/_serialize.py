from datetime import datetime
from inspect import isclass, getmodule
from typing import Any


SValue = str | int | float
SType = SValue | list["SType"] | dict[str, "SType"]
SList = list[SType]
SDict = dict[str, SType]


def serialize(obj: Any) -> SType:
    if isinstance(obj, int) or isinstance(obj, str) or isinstance(obj, float):
        return obj

    if isinstance(obj, datetime):
        return obj.isoformat()

    if isinstance(obj, list) or isinstance(obj, set):
        lobj: SList = []
        for x in sorted(obj):
            if not x or callable(x) or isclass(x):
                continue
            jx = serialize(x)
            if jx:
                lobj.append(jx)
        return lobj

    d: SDict = {}
    if isinstance(obj, dict):
        for k in sorted(obj.keys()):
            if k in ("model_fields_set", "permissions"):
                continue
            v = obj[k]
            if not v or callable(v) or isclass(v):
                continue
            jv = serialize(v)
            if jv:
                d[k] = jv
        return d

    for attrname in dir(obj):
        if attrname.startswith("_") or attrname.endswith("_"):
            continue
        if attrname in ("model_fields_set", "permissions"):
            continue
        attr = getattr(obj, attrname)
        if not attr or callable(attr) or isclass(attr):
            continue
        mod = getmodule(obj)
        if mod and "pydantic" in mod.__name__:
            continue
        jx = serialize(attr)
        if jx:
            d[attrname] = jx
    return d
