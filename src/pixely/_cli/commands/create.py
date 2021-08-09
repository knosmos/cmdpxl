# ========================= #
# CREATE COMMAND            #
# ========================= #

__command__ = "create"

from argparse import ArgumentParser
from typing import Optional, List
from pixely import Application

def main(
    argv: Optional[List[str]] = None
    ,pwd: str = None
    ,**kwargs
) -> bool:
    
    parser = ArgumentParser(
        prog="Create command"
        ,description="Create a workspace and initialize the image."
        ,add_help=True
    )

    parser.add_argument(
        'file'
        ,nargs=1
        ,type=str
        ,help="The file name to create."
    )

    parser.add_argument(
        'size'
        ,nargs=2
        ,type=int
        ,help="The size of the image to create"
    )

    args = parser.parse_args(argv)

    app = Application(
        filename=args.file[0],
        size=args.size,
        trigger="create"
    )

    app.start()

    return True