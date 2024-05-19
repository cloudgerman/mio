import click


class MioError(click.ClickException):
    def __init__(self, exit_code: int, name: str, msg: str) -> None:
        self.exit_code = exit_code
        self.name = name
        self.msg = msg
        super().__init__(f"[{name}] {msg}")


class GuardError(MioError):
    def __init__(self, msg: str) -> None:
        super().__init__(exit_code=10, name="guard:broken", msg=msg)


class ArgParsingError(MioError):
    def __init__(self, msg: str) -> None:
        super().__init__(exit_code=11, name="arg:parsing", msg=msg)


class CommandNotFoundError(MioError):
    def __init__(self, msg: str) -> None:
        super().__init__(exit_code=12, name="command:not-found", msg=msg)


class CommandError(MioError):
    def __init__(self, msg: str) -> None:
        super().__init__(exit_code=13, name="command:error", msg=msg)
