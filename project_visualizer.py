import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

def load_activities_from_json(file_path):
    """
    Loads activity data from a JSON file.

    :param file_path: Path to the JSON file.
    :return: A list of activity dictionaries.
    """
    try:
        with open(file_path, 'r') as f:
            activities = json.load(f)
        return activities
    except FileNotFoundError:
        print(f"Error: The file at {file_path} was not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: The file at {file_path} is not a valid JSON file.")
        return None

def load_activities_from_excel(file_path):
    """
    Loads activity data from an Excel file.
    Assumes the Excel file has columns corresponding to the activity dictionary keys.

    :param file_path: Path to the Excel file.
    :return: A list of activity dictionaries.
    """
    try:
        df = pd.read_excel(file_path)
        # The 'predecessors' and 'successors' columns might be strings of comma-separated values
        # or might not exist if there are no dependencies.
        if 'predecessors' in df.columns:
            df['predecessors'] = df['predecessors'].apply(lambda x: [p.strip() for p in str(x).split(',')] if pd.notna(x) and x != '' else [])
        if 'successors' in df.columns:
            df['successors'] = df['successors'].apply(lambda x: [s.strip() for s in str(x).split(',')] if pd.notna(x) and x != '' else [])

        return df.to_dict('records')
    except FileNotFoundError:
        print(f"Error: The file at {file_path} was not found.")
        return None
    except Exception as e:
        print(f"An error occurred while reading the Excel file: {e}")
        return None

def validate_activities(activities):
    """
    Validates the structure and content of the activity data.

    :param activities: A list of activity dictionaries.
    :return: A tuple (bool, str) indicating if validation passed and a message.
    """
    if not isinstance(activities, list):
        return False, "Input must be a list of activities."

    required_keys = {'id', 'name', 'Es', 'Duration', 'N', 'R', 'cost', 'predecessors', 'successors'}
    numeric_keys = {'Es', 'Duration', 'N', 'R', 'cost'}
    seen_ids = set()

    for i, activity in enumerate(activities):
        if not isinstance(activity, dict):
            return False, f"Activity at index {i} is not a valid dictionary."

        # Check for missing keys
        missing_keys = required_keys - set(activity.keys())
        if missing_keys:
            return False, f"Activity at index {i} is missing required keys: {missing_keys}"

        # Check for unique ID
        activity_id = activity['id']
        if activity_id in seen_ids:
            return False, f"Duplicate activity ID found: {activity_id}"
        seen_ids.add(activity_id)

        # Check numeric fields for non-negativity and valid types
        for key in numeric_keys:
            value = activity[key]
            if not isinstance(value, (int, float)) or value < 0:
                return False, f"Invalid value for '{key}' in activity '{activity_id}': must be a non-negative number."

    return True, "Validation successful."

def create_vertices_for_activities(activities):
    """
    Calculates parallelogram vertices for all activities using vectorized operations.

    :param activities: A list of activity dictionaries.
    :return: A list of activity dictionaries, each with a 'vertices' key.
    """
    if not activities:
        return []

    # Extract data into NumPy arrays for vectorized calculations
    es_values = np.array([a['Es'] for a in activities])
    duration_values = np.array([a['Duration'] for a in activities])
    n_values = np.array([a['N'] for a in activities])
    r_values = np.array([a['R'] for a in activities])

    # Calculate p3_x using vectorized operations
    # np.divide with a where clause handles the R=0 case to avoid division by zero.
    p3_x = np.divide(n_values - 1, r_values, out=np.zeros_like(r_values), where=r_values!=0) + es_values

    # Assemble vertices for all activities at once
    # Each row in the vertices_stack corresponds to an activity
    # The structure is [p1_x, p1_y, p2_x, p2_y, p3_x, p3_y, p4_x, p4_y]
    vertices_stack = np.vstack([
        es_values, np.zeros_like(es_values),
        es_values + duration_values, np.zeros_like(es_values),
        p3_x, n_values,
        p3_x + duration_values, n_values
    ]).T

    # Reshape to get a (num_activities, 4, 2) array
    vertices_array = vertices_stack.reshape(-1, 4, 2)

    # Append vertices to each activity dictionary
    for i, activity in enumerate(activities):
        activity['vertices'] = vertices_array[i].tolist()

    return activities

def plot_multiple_parallelograms(activity_data_list, title="Project Activity Parallelograms", output_file=None, max_to_plot=1000):
    """
    Renders parallelograms for all activities on a single Matplotlib plot.

    :param activity_data_list: List of processed activity dictionaries with 'vertices'.
    :param title: The title for the plot.
    :param output_file: Optional path to save the plot image. If None, displays the plot.
    :param max_to_plot: Maximum number of activities to plot to prevent performance issues.
    """
    if not activity_data_list:
        print("No activities to plot.")
        return

    fig, ax = plt.subplots(figsize=(14, 8))

    # Limit the number of activities to plot for performance
    if len(activity_data_list) > max_to_plot:
        print(f"Warning: Dataset contains {len(activity_data_list)} activities, but only plotting the first {max_to_plot}.")
        activity_data_list = activity_data_list[:max_to_plot]

    # Define a color cycle for the patches
    colors = plt.colormaps.get_cmap('hsv', len(activity_data_list))

    all_vertices = []
    for i, activity in enumerate(activity_data_list):
        vertices = np.array(activity['vertices'])
        all_vertices.append(vertices)

        patch = Polygon(
            vertices,
            closed=True,
            facecolor=colors(i),
            edgecolor='black',
            alpha=0.7,
            label=activity.get('id', 'N/A')
        )
        ax.add_patch(patch)

    if not all_vertices:
        print("No vertices found to plot.")
        return

    # Set axis limits dynamically
    all_vertices_np = np.concatenate(all_vertices)
    x_min, y_min = np.min(all_vertices_np, axis=0)
    x_max, y_max = np.max(all_vertices_np, axis=0)

    ax.set_xlim(x_min - (x_max - x_min) * 0.05, x_max + (x_max - x_min) * 0.05)
    ax.set_ylim(y_min, y_max + (y_max - y_min) * 0.05)

    # Configure plot
    ax.set_aspect('equal', adjustable='box')
    ax.set_xlabel("Time")
    ax.set_ylabel("Resource/Height")
    ax.set_title(title)
    ax.grid(True, linestyle='--', alpha=0.6)

    # Optional legend (can be crowded with many activities)
    if len(activity_data_list) <= 20: # Only show legend for a small number of activities
        ax.legend(title="Activity IDs")

    # Handle output
    if output_file:
        plt.savefig(output_file, dpi=300)
        print(f"Plot saved to {output_file}")
    else:
        plt.show()

def save_activities_to_json(activities, file_path=None):
    """
    Saves the processed activity data to a JSON file or returns it as a string.

    :param activities: The list of activity dictionaries with vertices.
    :param file_path: Optional path to the output JSON file. If None, returns a JSON string.
    :return: JSON string if file_path is None, otherwise None.
    """
    if file_path:
        with open(file_path, 'w') as f:
            json.dump(activities, f, indent=2)
        print(f"Activity data saved to {file_path}")
    else:
        # Return as a formatted string
        return json.dumps(activities, indent=2)

def generate_sample_activities(num_activities):
    """
    Generates a list of sample activities for testing.

    :param num_activities: The number of sample activities to generate.
    :return: A list of activity dictionaries.
    """
    activities = []
    for i in range(num_activities):
        activity = {
            "id": f"A{i+1}",
            "name": f"Activity {i+1}",
            "Es": np.random.uniform(0, 50),
            "Duration": np.random.uniform(5, 20),
            "N": np.random.uniform(1, 10),
            "R": np.random.uniform(0, 5),
            "cost": np.random.uniform(100, 1000),
            "predecessors": [f"A{j}" for j in range(i) if np.random.rand() > 0.8], # Random predecessors
            "successors": [] # Successors can be populated later if needed
        }
        activities.append(activity)
    return activities

if __name__ == '__main__':
    # This block demonstrates the full workflow of the module.

    # --- Configuration ---
    NUM_ACTIVITIES_TO_GENERATE = 50
    OUTPUT_PLOT_FILE = "project_activities.png"
    OUTPUT_JSON_FILE = "processed_activities.json"

    print("--- Project Visualizer Demonstration ---")

    # 1. Generate a sample dataset
    print(f"\n1. Generating a sample dataset of {NUM_ACTIVITIES_TO_GENERATE} activities...")
    sample_activities = generate_sample_activities(NUM_ACTIVITIES_TO_GENERATE)
    print("Sample dataset created.")

    # 2. Validate the generated data
    print("\n2. Validating data...")
    is_valid, message = validate_activities(sample_activities)
    if not is_valid:
        print(f"Validation Error: {message}")
        # Exit if validation fails
    else:
        print("Data validation successful.")

        # 3. Calculate vertices for all activities
        print("\n3. Calculating vertices...")
        processed_activities = create_vertices_for_activities(sample_activities)
        print(f"Calculated vertices for {len(processed_activities)} activities.")

        # 4. Plot the activities and save to a file
        print(f"\n4. Generating plot and saving to '{OUTPUT_PLOT_FILE}'...")
        plot_multiple_parallelograms(
            processed_activities,
            title=f"Visualization of {len(processed_activities)} Project Activities",
            output_file=OUTPUT_PLOT_FILE
        )

        # 5. Save the processed data to a JSON file
        print(f"\n5. Saving processed data to '{OUTPUT_JSON_FILE}'...")
        save_activities_to_json(processed_activities, OUTPUT_JSON_FILE)

        print("\n--- Workflow Complete ---")
