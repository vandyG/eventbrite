"""This module provides functions for generating visualizations from Eventbrite attendee data.

It includes functions to load and preprocess data, as well as generate
visualizations for events per month, attendees per event, and frequent attendees.
The module is designed to be integrated with a CLI, allowing for flexible
input and output path specification and optional logging.
"""

import logging
from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from rich import print


def load_data(file_path: Path, logger: Optional[logging.Logger] = None) -> pd.DataFrame:
    """Loads data from a CSV file into a Pandas DataFrame.

    Args:
        file_path: The path to the CSV file (as a pathlib.Path object).
        logger: An optional logger for logging messages.

    Returns:
        A Pandas DataFrame containing the data.
        Returns None and logs an error if the file does not exist or if an error occurs during loading.
    """
    if not file_path.exists():
        if logger:
            logger.error(f"Error: The file '{file_path}' was not found.")
        else:
            print(f"Error: The file '{file_path}' was not found.")
        return None

    return pd.read_csv(file_path)


def preprocess_data(df: pd.DataFrame, logger: Optional[logging.Logger] = None) -> pd.DataFrame:
    """Preprocesses the input DataFrame by converting date columns and extracting features.

    Args:
        df: The input Pandas DataFrame.
        logger: An optional logger for logging messages.

    Returns:
        The preprocessed Pandas DataFrame.
    """
    df["event_start"] = pd.to_datetime(df["event_start"])
    df["event_year"] = df["event_start"].dt.year
    df["event_month"] = df["event_start"].dt.month
    df["event_month_name"] = df["event_start"].dt.strftime("%b")  # Abbreviated month name

    #  Use max() to get the latest year
    current_year_in_data = df["event_year"].max()
    if logger:
        logger.info(f"Analyzing data for the year: {current_year_in_data}")
    else:
        print(f"Analyzing data for the year: {current_year_in_data}")

    return df


def visualize_events_per_month(df: pd.DataFrame, save_path: Path, logger: Optional[logging.Logger] = None) -> None:
    """Generates a line chart visualizing the total number of unique events per month.

    Args:
        df: The Pandas DataFrame containing event data.
        save_path: The path to save the generated plot (as a pathlib.Path object).
        logger: An optional logger for logging messages.
    """
    events_per_month = df.groupby(df["event_start"].dt.to_period("M"))["event_id"].nunique().reset_index()
    events_per_month["event_start"] = events_per_month["event_start"].dt.to_timestamp()
    events_per_month = events_per_month.sort_values("event_start")

    plt.figure(figsize=(12, 6))
    sns.lineplot(x="event_start", y="event_id", data=events_per_month, marker="o")
    plt.title("Total Number of Unique Events Per Month")
    plt.xlabel("Month")
    plt.ylabel("Number of Unique Events")
    plt.grid(visible=True, linestyle="--", alpha=0.7)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(str(save_path))  # Convert Path to string for savefig
    if logger:
        logger.info(f"Events per month visualization saved to {save_path}")
    else:
        print(f"Events per month visualization saved to {save_path}")



def visualize_attendees_per_event(df: pd.DataFrame, save_path: Path, logger: Optional[logging.Logger] = None) -> None:
    """Generates a bar graph visualizing the number of attendees in each event for the current year.

    Args:
        df: The Pandas DataFrame containing event data.
        save_path: The path to save the generated plot (as a pathlib.Path object).
        logger: An optional logger for logging messages.
    """
    current_year_in_data = df["event_year"].max()
    df_current_year = df[df["event_year"] == current_year_in_data].copy()
    attendees_per_event = (
        df_current_year.groupby(["event_name", "event_id"]).size().reset_index(name="attendee_count")
    )
    attendees_per_event = attendees_per_event.sort_values("attendee_count", ascending=False)

    plt.figure(figsize=(14, 7))
    sns.barplot(
        x="event_name",
        y="attendee_count",
        data=attendees_per_event,
        palette="viridis",
        hue="event_name",
        legend=False,
    )
    plt.title(f"Number of Attendees Per Event in {current_year_in_data}")
    plt.xlabel("Event Name")
    plt.ylabel("Number of Attendees")
    plt.xticks(rotation=60, ha="right")
    plt.tight_layout()
    plt.savefig(str(save_path))  # Convert Path to string for savefig
    if logger:
        logger.info(f"Attendees per event visualization saved to {save_path}")
    else:
        print(f"Attendees per event visualization saved to {save_path}")

def visualize_frequent_attendees(df: pd.DataFrame, save_path: Path, logger: Optional[logging.Logger] = None) -> None:
    """Generates a bar chart visualizing the top 10 most frequent attendees.

    Args:
        df: The Pandas DataFrame containing attendee data.
        save_path: The path to save the generated plot (as a pathlib.Path object).
        logger: An optional logger for logging messages.
    """
    frequent_attendees = (
        df[
            (df["attendee_name"] != "Info Requested")
            & (df["attendee_name"].notna())
            & (df["email"] != "Info Requested")
            & (df["email"].notna())
        ]
        .groupby(["attendee_name", "email"])["event_id"]
        .nunique()
        .reset_index(name="events_attended")
    )

    frequent_attendees = frequent_attendees.sort_values("events_attended", ascending=False).head(10)
    frequent_attendees["display_name"] = frequent_attendees["attendee_name"]

    if not frequent_attendees.empty:
        plt.figure(figsize=(12, 6))
        sns.barplot(
            x="display_name",
            y="events_attended",
            data=frequent_attendees,
            palette="magma",
            hue="display_name",
            legend=False,
        )
        plt.title("Top 10 Most Frequent Attendees (by Unique Events Attended)")
        plt.xlabel("Attendee Name")
        plt.ylabel("Number of Unique Events Attended")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig(str(save_path))  # Convert Path to string for savefig
        if logger:
            logger.info(f"Frequent attendees visualization saved to {save_path}")
        else:
            print(f"Frequent attendees visualization saved to {save_path}")
    elif logger:
        logger.warning("No frequent attendee data to display (perhaps no valid names/emails found).")
    else:
        print("No frequent attendee data to display (perhaps no valid names/emails found).")


def generate_visualizations(file_path: Path, output_dir: Path, logger: Optional[logging.Logger] = None) -> None:
    """Generates and saves visualizations from the Eventbrite attendee data.

    Args:
        file_path: The path to the attendees CSV file (as a pathlib.Path object).
        output_dir: The directory where the visualizations should be saved (as a pathlib.Path object).
        logger: An optional logger for logging messages.
    """
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)  # Create dir and parents if needed
        if logger:
            logger.info(f"Output directory '{output_dir}' created.")
        else:
            print(f"Output directory '{output_dir}' created.")

    df = load_data(file_path, logger)
    if df is None:
        return

    df = preprocess_data(df, logger)
    if df is None:
        return

    visualize_events_per_month(df, output_dir / "events_per_month.svg", logger)
    visualize_attendees_per_event(df, output_dir / "attendees.svg", logger)
    visualize_frequent_attendees(df, output_dir / "frequent.svg", logger)


if __name__ == "__main__":
    # Example usage with basic logging
    import logging

    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    logger = logging.getLogger(__name__)
    generate_visualizations(
        file_path=Path("data/attendees.csv"),
        output_dir=Path("output"),
        logger=logger,
    )
