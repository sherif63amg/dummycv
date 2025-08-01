import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# 1. قسم البيانات (Data Layer)
# -------------------------------------------------------------
total_units = 20

# 'duration' is now the input instead of 'production_rate'
activities_data = {
    "Foundation": {
        "initial_start_day": 0,
        "duration": 10,  # Total duration to complete 20 units
        "predecessor": None,
        "buffer_days": 2  # Buffer after this activity
    },
    "Framing": {
        "duration": 8,  # Total duration to complete 20 units
        "predecessor": "Foundation",
        "buffer_days": 3
    },
    "Roofing": {
        "duration": 5,  # Total duration to complete 20 units
        "predecessor": "Framing",
        "buffer_days": 2
    },
    "Finishing": {
        "duration": 6,  # Total duration to complete 20 units
        "predecessor": "Roofing",
        "buffer_days": 0
    }
}

# 2. قسم المنطق (Business Logic Layer)
# -------------------------------------------------------------
def prepare_parallelogram_data(activities, total_units, lag_time=0.5):
    """
    Calculates the parallelogram vertex coordinates for each activity based on
    Line of Balance logic, including dependencies, durations, and buffers.

    :param activities: Dictionary containing activity data.
    :param total_units: Total number of units in the project.
    :param lag_time: Visual lag time to shift the parallelogram.
    :return: A list of dictionaries with activity name and coordinates.
    """
    processed_data = []
    # This dictionary will store calculated data for each activity
    # to be used by its successors.
    calculated_activity_data = {}

    for activity_name, data in activities.items():
        duration = data["duration"]
        rate = total_units / duration if duration > 0 else 0

        predecessor_name = data["predecessor"]

        if predecessor_name is None:
            # First activity
            start_day_unit1 = data.get("initial_start_day", 0)
        else:
            # Successor activity
            pred_data = calculated_activity_data[predecessor_name]
            pred_rate = pred_data["rate"]
            pred_start_day_unit1 = pred_data["start_day_unit1"]
            pred_buffer = activities[predecessor_name]["buffer_days"]

            # Time when predecessor finishes unit 1
            pred_end_day_unit1 = pred_start_day_unit1 + (1 / pred_rate if pred_rate > 0 else 0)

            if rate > pred_rate:
                # Current activity is faster than predecessor, constraint is at the last unit.
                # We calculate when the predecessor finishes the last unit.
                pred_end_day_last_unit = pred_start_day_unit1 + (total_units / pred_rate if pred_rate > 0 else 0)

                # The start of the current activity on unit 1 is determined by the completion
                # of the predecessor on the last unit, plus buffer.
                start_day_unit1 = pred_end_day_last_unit + pred_buffer - ((total_units - 1) / rate if rate > 0 else 0)

            else:
                # Current activity is slower or same speed, constraint is at the first unit.
                start_day_unit1 = pred_end_day_unit1 + pred_buffer

        # The overall end day is when the activity finishes for the last unit.
        end_day_last_unit = start_day_unit1 + duration

        # Store calculated values for successors
        calculated_activity_data[activity_name] = {
            "rate": rate,
            "start_day_unit1": start_day_unit1,
            "end_day_last_unit": end_day_last_unit,
        }

        # Define the vertices of the parallelogram.
        # The start_day is the start on unit 1.
        # The end_day is the completion of the last unit.
        vertices = [
            (start_day_unit1, 0),
            (end_day_last_unit, total_units),
            (end_day_last_unit + lag_time, total_units),
            (start_day_unit1 + lag_time, 0)
        ]

        processed_data.append({
            "name": activity_name,
            "vertices": vertices,
            "start_day": start_day_unit1,
            "end_day": end_day_last_unit
        })

    return processed_data

# 3. قسم العرض (Presentation Layer)
# -------------------------------------------------------------
def plot_lob_chart(processed_data, total_units):
    """
    يرسم مخطط Line of Balance باستخدام البيانات المعالجة.

    :param processed_data: قائمة بالبيانات المحسوبة للرسم.
    :param total_units: إجمالي عدد الوحدات.
    """
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.set_title("Line of Balance Chart: Duration is Input")
    ax.set_xlabel("Time (Days)")
    ax.set_ylabel("Number of Units")
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    ax.set_yticks(range(0, total_units + 1, 5))

    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']

    for idx, item in enumerate(processed_data):
        parallelogram = patches.Polygon(
            item["vertices"],
            closed=True,
            edgecolor='black',
            facecolor=colors[idx % len(colors)],
            alpha=0.6,
            label=item["name"]
        )
        ax.add_patch(parallelogram)

    max_end_day = max(item["end_day"] for item in processed_data)
    ax.set_xlim(0, max_end_day + 5)
    ax.set_ylim(0, total_units + 2)

    x_ticks = np.arange(0, int(max_end_day) + 5, 2)
    ax.set_xticks(x_ticks)
    ax.minorticks_on()
    ax.xaxis.set_minor_locator(plt.MultipleLocator(1))

    ax.legend()
    plt.show()

# 4. الجزء التنفيذي الرئيسي
# -------------------------------------------------------------
if __name__ == "__main__":
    processed_activities = prepare_parallelogram_data(activities_data, total_units)
    plot_lob_chart(processed_activities, total_units)
