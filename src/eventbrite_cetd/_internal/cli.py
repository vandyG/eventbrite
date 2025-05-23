"""CLI interface for the Eventbrite Attendee Exporter.

This module provides a command-line interface for the Eventbrite Attendee Exporter,
allowing users to fetch attendee data for their organizations and export it to a CSV file.
"""

import asyncio
import logging
from pathlib import Path
from typing import Annotated

import typer
from rich import console
from rich.logging import RichHandler

from eventbrite_cetd._internal import debug
from eventbrite_cetd._internal.eventbrite import main  # Import the main function from eventbrite.py
from eventbrite_cetd._internal.visualisation import generate_visualizations

app = typer.Typer()
rich_console = console.Console()


def version_callback(value: bool) -> None:  # noqa: FBT001
    """Callback function to handle the --version flag.

    Args:
        value (bool): Boolean indicating if the version flag is present.

    Raises:
        typer.Exit: Exits the application after printing the version.
    """
    if value:
        rich_console.print(f"eventbrite-cetd version: {debug._get_version()}")
        raise typer.Exit


def debug_callback(value: bool) -> None:  # noqa: FBT001
    if value:
        debug._print_debug_info()
        raise typer.Exit


@app.callback()
def common(
    version: bool = typer.Option(None, "-V", "--version", callback=version_callback, help="Show version and exit."),  # noqa: FBT001
    debug_info: bool = typer.Option(  # noqa: FBT001
        None, "-D", "--debug-info", callback=debug_callback, help="Show debug information and exit.",
    ),
) -> None:
    """CLI interface for the Eventbrite Attendee Exporter.

    Command-line interface for the Eventbrite Attendee Exporter,
    allowing users to fetch attendee data for their organizations and export it to a CSV file.
    """


@app.command()
def generate(
    output_file: str = typer.Option("data/attendees.csv", help="Path to the output CSV file."),
) -> None:
    """Fetch and export Eventbrite attendee data.

    Args:
        output_file (str, optional): Path to the output CSV file. Defaults to "data/attendees.csv".
    """
    # Configure logging with rich
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=rich_console)],
    )
    logger = logging.getLogger("eventbrite-cetd")

    try:
        asyncio.run(main(logger, output_file))
        rich_console.print("[bold green]Attendee data export completed successfully![/bold green]")
    except Exception as e:
        logger.exception("[bold red]An error occurred:[/bold red]")
        raise typer.Exit(code=1) from e


@app.command()
def visualize(
    input_file: Annotated[
        Path,
        typer.Option(
            help="Path to the input CSV file for visualization.",
            file_okay=True,
            dir_okay=False,
            writable=False,
            readable=True,
        ),
    ] = Path("./data/attendees.csv"),
    output_dir: Annotated[
        Path,
        typer.Option(
            help="Directory to save the generated visualizations.",
            file_okay=False,
            dir_okay=True,
            readable=True,
        ),
    ] = Path("./data"),
) -> None:
    """Generate visualizations from Eventbrite attendee data.

    Args:
        input_file (Path, optional): Path to the input CSV file. Defaults to "data/attendees.csv".
        output_dir (Path, optional): Directory to save the visualizations. Defaults to "output".
    """
    # Configure logging with rich (reusing the same configuration as generate command)
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=rich_console)],
    )
    logger = logging.getLogger("eventbrite-cetd.visualize")

    try:
        generate_visualizations(file_path=Path(input_file), output_dir=Path(output_dir), logger=logger)
        rich_console.print("[bold green]Visualizations generated successfully![/bold green]")
    except Exception as e:
        logger.exception("[bold red]An error occurred during visualization:[/bold red]")
        raise typer.Exit(code=1) from e


if __name__ == "__main__":
    app()
