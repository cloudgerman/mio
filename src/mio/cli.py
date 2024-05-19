import click

from .cli_imap import imap


@click.group()
def main() -> None:
    pass


main.add_command(imap)
