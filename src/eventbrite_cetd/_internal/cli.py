# Why does this file exist, and why not put this in `__main__`?
#
# You might be tempted to import things from `__main__` later,
# but that will cause problems: the code will get executed twice:
#
# - When you run `python -m eventbrite_cetd` python will execute
#   `__main__.py` as a script. That means there won't be any
#   `eventbrite_cetd.__main__` in `sys.modules`.
# - When you import `__main__` it will get executed again (as a module) because
#   there's no `eventbrite_cetd.__main__` in `sys.modules`.

from __future__ import annotations

import argparse
import sys
from typing import Any

import typer

from eventbrite_cetd._internal import debug
from eventbrite_cetd.eventbrite import get_my_organizations


class _DebugInfo(argparse.Action):
    def __init__(self, nargs: int | str | None = 0, **kwargs: Any) -> None:
        super().__init__(nargs=nargs, **kwargs)

    def __call__(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        debug._print_debug_info()
        sys.exit(0)


def get_parser() -> argparse.ArgumentParser:
    """Return the CLI argument parser.

    Returns:
        An argparse parser.
    """
    parser = argparse.ArgumentParser(prog="eventbrite-cetd")
    parser.add_argument("-V", "--version", action="version", version=f"%(prog)s {debug._get_version()}")
    parser.add_argument("--debug-info", action=_DebugInfo, help="Print debug information.")
    parser.add_argument(
        "-o",
        "--organization",
        action=_DebugInfo,
        help="Organization to fetch events for.",
        type=int,
        default=0,
    )
    return parser


def main(organizaiton: int = 0, debug_info: ) -> int:
    """Run the main program.

    This function is executed when you type `eventbrite-cetd` or `python -m eventbrite_cetd`.

    Parameters:
        args: Arguments passed from the command line.

    Returns:
        An exit code.
    """
    parser = get_parser()
    opts = parser.parse_args(args=args)
    if not opts.organization:
        organizations = get_my_organizations()

        if not organizations:
            print("No organizations found.")
            return 1

        print("Select an organization:")
        for i, org in enumerate(organizations, 1):
            print(f"{i}: {org['name']} (ID: {org['id']})")

        while True:
            try:
                selection = int(input("Enter the number of the organization: "))
                if 1 <= selection <= len(organizations):
                    selected_org_id = organizations[selection - 1]["id"]
                    break
                print("Invalid selection. Try again.")
            except ValueError:
                print("Please enter a valid number.")

        print(f"Selected organization ID: {selected_org_id}")
        # Use selected_org_id as needed
    else:
        selected_org_id = opts.organization
        print(f"Organization ID provided via CLI: {selected_org_id}")
    return 0


app = typer.Typer()
app.command()(main)
