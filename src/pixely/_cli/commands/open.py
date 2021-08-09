# ========================= #
# OPEN COMMAND              #
# ========================= #

__command__ = "open"

from argparse import ArgumentParser
from typing import Optional, List
from pixely import Application

def main(
    argv: Optional[List[str]] = None
    ,pwd: str = None
    ,**kwargs
) -> bool:
    
    parser = ArgumentParser(
        prog="Open command"
        ,description="Open an image and use it."
        ,add_help=True
    )

    parser.add_argument(
        'file'
        ,nargs=1
        ,type=str
        ,help="The file to open."
    )

    args = parser.parse_args(argv)

    app = Application(
        filename=args.file[0],
        trigger="open"
    )

    app.start()

    return True