from mio import error


def test_exceptions() -> None:
    error_codes: set[int] = set()

    for name in dir(error):
        attr = getattr(error, name)
        if not isinstance(attr, type):
            continue
        if hasattr(attr, "__mro__") and error.MioError in attr.__mro__:
            if attr == error.MioError:
                continue
            e = attr(msg="error ")
            assert e.exit_code not in error_codes
            error_codes.add(e.exit_code)
