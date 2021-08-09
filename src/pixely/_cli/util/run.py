# ========================= #
# RUN METHOD                #
# ========================= #

from typing import List
from importlib import import_module
from .. import META_COMMANDS

def run_subcommand(
    subcommand: str
    ,subcommand_args: List[str] = None
    ,pwd: str = None
    ,**kwargs
):
    """
    Run the given command.
    """

    subcommand_args = subcommand_args or []

    if subcommand not in META_COMMANDS:
        return False

    module = import_module(
        "gpip._cli.commands.{}".format(subcommand)
        ,__package__
    )
    
    return module.main(
        argv=subcommand_args
        ,pwd=pwd
        ,**kwargs
    )