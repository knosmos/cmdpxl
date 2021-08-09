import sys
import os

from .util.run import run_subcommand
from argparse import ArgumentParser

def main():

    parser = ArgumentParser()

    # ========================= #
    # COMMAND ENTRIES           #
    # ========================= #

    parser.add_argument(
        'subcommand'
        ,nargs=1
        ,type=str
        ,help="The command to be executed."
    )

    parser.add_argument(
        'subcommand_args'
        ,nargs="*"
        ,type=str
        ,help="The command arguments to be used by the subcommand."
    )
    
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    
    argv = sys.argv[1:]
    args = parser.parse_args(argv)

    if not run_subcommand(
        subcommand=args.subcommand[0].lower()
        ,subcommand_args=args.subcommand_args
        ,pwd=os.getcwd()
    ):
        parser.print_help()