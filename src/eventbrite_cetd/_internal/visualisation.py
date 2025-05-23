import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def generate_visualizations(file_path="attendees.csv"):
    """Generates and displays visualizations from the Eventbrite attendee data.

    Args:
        file_path (str): The path to the attendees CSV file.
    """
    if not os.path.exists(file_path):
        print(f"Error: The file '{file_path}' was not found.")
        return

    try:
        # Load the dataset
        df = pd.read_csv(file_path)

        # --- Data Preprocessing ---
        # Convert 'event_start' to datetime objects
        df["event_start"] = pd.to_datetime(df["event_start"])

        # Extract year and month for time-based analysis
        df["event_year"] = df["event_start"].dt.year
        df["event_month"] = df["event_start"].dt.month
        df["event_month_name"] = df["event_start"].dt.strftime("%b") # Abbreviated month name

        # Get the current year from the data (assuming data is mostly from one year or we want the latest)
        # Or, if the data spans multiple years, we can pick the latest year present in the data.
        current_year_in_data = df["event_year"].max()
        print(f"Analyzing data for the year: {current_year_in_data}")

        # --- Visualization 1: Total Number of Events Per Month (Line Chart) ---
        # Count unique events per month (across all years or specific year if filtered)
        # For this example, we'll count unique events per month-year combination
        events_per_month = df.groupby([df["event_start"].dt.to_period("M")])["event_id"].nunique().reset_index()
        events_per_month["event_start"] = events_per_month["event_start"].dt.to_timestamp() # Convert Period back to Timestamp for plotting
        events_per_month = events_per_month.sort_values("event_start")

        plt.figure(figsize=(12, 6))
        sns.lineplot(x="event_start", y="event_id", data=events_per_month, marker="o")
        plt.title("Total Number of Unique Events Per Month")
        plt.xlabel("Month")
        plt.ylabel("Number of Unique Events")
        plt.grid(True, linestyle="--", alpha=0.7)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

        # --- Visualization 2: Number of Attendees in Each Event in Current Year (Bar Graph) ---
        # Filter data for the current year
        df_current_year = df[df["event_year"] == current_year_in_data].copy()

        # Count attendees per unique event in the current year
        # We'll use event_name and event_id to uniquely identify events.
        # Assuming each row is a unique attendee registration for an event.
        attendees_per_event = df_current_year.groupby(["event_name", "event_id"]).size().reset_index(name="attendee_count")
        attendees_per_event = attendees_per_event.sort_values("attendee_count", ascending=False)

        plt.figure(figsize=(14, 7))
        sns.barplot(x="event_name", y="attendee_count", data=attendees_per_event, palette="viridis")
        plt.title(f"Number of Attendees Per Event in {current_year_in_data}")
        plt.xlabel("Event Name")
        plt.ylabel("Number of Attendees")
        plt.xticks(rotation=60, ha="right") # Rotate labels for better readability
        plt.tight_layout()
        plt.show()

        # --- New Visualization: Most Frequent Attendees (Bar Chart) ---
        # Count the number of events each unique attendee (identified by email) has attended.
        # Filter out any 'Info Requested' or empty emails if they exist.
        frequent_attendees = df[df["email"] != "Info Requested"].groupby("email")["event_id"].nunique().reset_index(name="events_attended")
        frequent_attendees = frequent_attendees.sort_values("events_attended", ascending=False).head(10) # Get top 10

        if not frequent_attendees.empty:
            plt.figure(figsize=(12, 6))
            sns.barplot(x="email", y="events_attended", data=frequent_attendees, palette="magma")
            plt.title("Top 10 Most Frequent Attendees (by Unique Events Attended)")
            plt.xlabel("Attendee Email")
            plt.ylabel("Number of Unique Events Attended")
            plt.xticks(rotation=45, ha="right")
            plt.tight_layout()
            plt.show()
        else:
            print("No frequent attendee data to display (perhaps no valid emails found).")


    except Exception as e:
        print(f"An error occurred during visualization generation: {e}")

if __name__ == "__main__":
    generate_visualizations()
