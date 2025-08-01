import matplotlib.pyplot as plt
import matplotlib.patches as patches
from datetime import datetime, timedelta

def plot_line_of_balance(activities, num_units):
    """
    Plots a Line of Balance chart with trapezoidal shapes for each activity.

    Args:
        activities (list): A list of dictionaries, where each dictionary
                           represents an activity and contains the following keys:
                           'name': Name of the activity (str).
                           'start_date': Start date of the first unit (str, 'YYYY-MM-DD').
                           'duration_per_unit': Time to complete one unit in days (int).
                           'lag_between_units': Time lag between starting consecutive units in days (int).
        num_units (int): The total number of repetitive units.
    """
    fig, ax = plt.subplots(figsize=(15, 10))

    # Set up the axes
    ax.set_xlabel("Time")
    ax.set_ylabel("Unit Number")
    ax.set_title("Line of Balance Chart")
    ax.set_ylim(0, num_units + 1)
    ax.set_yticks(range(1, num_units + 1))
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)

    date_format = "%Y-%m-%d"
    min_date = None
    max_date = None

    colormap = plt.colormaps.get_cmap('viridis')
    colors = [colormap(i / len(activities)) for i in range(len(activities))]

    for i, activity in enumerate(activities):
        start_date_first_unit = datetime.strptime(activity['start_date'], date_format)
        duration = timedelta(days=activity['duration_per_unit'])
        lag = timedelta(days=activity['lag_between_units'])

        # Calculate the four points of the main trapezoid for the whole activity
        # Point 1: Start of activity on unit 1
        p1_date = start_date_first_unit

        # Point 2: Finish of activity on unit 1
        p2_date = start_date_first_unit + duration

        # Point 3: Start of activity on the last unit
        p3_date = start_date_first_unit + (num_units - 1) * lag

        # Point 4: Finish of activity on the last unit
        p4_date = p3_date + duration

        # Convert dates to numerical format for plotting
        p1_num = (p1_date - datetime(1970, 1, 1)).days
        p2_num = (p2_date - datetime(1970, 1, 1)).days
        p3_num = (p3_date - datetime(1970, 1, 1)).days
        p4_num = (p4_date - datetime(1970, 1, 1)).days

        # Define the vertices of the trapezoid representing the "line"
        line_verts = [
            (p1_num, 1),
            (p3_num, num_units),
            (p4_num, num_units),
            (p2_num, 1)
        ]

        polygon = patches.Polygon(line_verts, closed=True, facecolor=colors[i], alpha=0.5, label=activity['name'])
        ax.add_patch(polygon)

        # Update min and max dates for x-axis limits
        current_min_date = p1_date
        current_max_date = p4_date

        if min_date is None or current_min_date < min_date:
            min_date = current_min_date
        if max_date is None or current_max_date > max_date:
            max_date = current_max_date

    # Format x-axis to show dates
    if min_date and max_date:
        start_num = (min_date - timedelta(days=5) - datetime(1970, 1, 1)).days
        end_num = (max_date + timedelta(days=5) - datetime(1970, 1, 1)).days
        ax.set_xlim(start_num, end_num)

        # Create a list of tick locations and labels
        tick_dates = []
        current_date = min_date - timedelta(days=5)
        while current_date <= max_date + timedelta(days=5):
            tick_dates.append(current_date)
            current_date += timedelta(days=7) # Weekly ticks

        ax.set_xticks([(d - datetime(1970, 1, 1)).days for d in tick_dates])
        ax.set_xticklabels([d.strftime('%Y-%m-%d') for d in tick_dates], rotation=45, ha='right')

    ax.legend()
    plt.tight_layout()

    # Save the plot to a file
    plt.savefig('line_of_balance.png')
    print("Plot saved as line_of_balance.png")

if __name__ == '__main__':
    # Example Data
    NUMBER_OF_UNITS = 10

    ACTIVITIES = [
        {
            'name': 'Excavation',
            'start_date': '2024-01-01',
            'duration_per_unit': 2,
            'lag_between_units': 1,
        },
        {
            'name': 'Foundation',
            'start_date': '2024-01-05',
            'duration_per_unit': 3,
            'lag_between_units': 2,
        },
        {
            'name': 'Framing',
            'start_date': '2024-01-15',
            'duration_per_unit': 5,
            'lag_between_units': 3,
        },
        {
            'name': 'Roofing',
            'start_date': '2024-02-01',
            'duration_per_unit': 4,
            'lag_between_units': 2,
        },
    ]

    plot_line_of_balance(ACTIVITIES, NUMBER_OF_UNITS)
