# ========================= #
# START COMMAND             #
# ========================= #

__command__ = "start"

from argparse import ArgumentParser
from typing import Optional, List
from pixely import Application

def main(
    argv: Optional[List[str]] = None
    ,pwd: str = None
    ,**kwargs
) -> bool:
    app = Application()
    app.start()
    return True