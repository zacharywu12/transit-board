from bike import get_station_bike_availability
from muni import MuniAPI
from typing import Dict
import time
import os
from datetime import datetime

# Configuration
target_stations_shortnames = ["SF-F23-2", "SF-F23-3", "SF-F23", "SF-F24"]

# Muni stop IDs and their descriptions
target_stops = [
    "18092",
    "18101",
    "16303",
    "14022",
    "13812",
    "16597",
    "16016",
    "15813",
    "14302",
    "16002",
    "15995",
]
num_predictions = 3  # Number of predictions to show per route/direction

def format_bike_table(stations: Dict[str, dict]) -> str:
    """
    Format station information as a simple ASCII table.
    """
    # Define column widths
    name_width = max(len(info['name']) for info in stations.values())
    name_width = max(name_width, 20)  # minimum width
    
    # Create header
    header = f"| {'Station Name':<{name_width}} | {'Regular':<8} | {'E-Bikes':<8} |"
    separator = f"|{'-' * (name_width + 2)}|{'-' * 10}|{'-' * 10}|"
    
    # Create rows
    rows = []
    for info in stations.values():
        row = f"| {info['name']:<{name_width}} | {info['bikes_available']:^8} | {info['ebikes_available']:^8} |"
        rows.append(row)
    
    # Combine all parts
    table = "\n".join([header, separator] + rows)
    return table

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    # Initialize APIs
    muni = MuniAPI()
    
    try:
        while True:
            try:
                clear_screen()
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # Get and display bike information
                print(f"\nLast updated: {current_time} PST")
                print("\nBike Share Status:")
                stations = get_station_bike_availability(target_stations_shortnames)
                print(format_bike_table(stations))
                
                # Get and display Muni predictions
                print("\nMuni Predictions:")
                predictions = muni.get_stop_predictions(target_stops, num_predictions)
                print(muni.format_predictions(predictions))
                print()  # Empty line for spacing
                
                # Wait before next update
                time.sleep(30)
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(5)  # Wait a bit before retrying if there's an error
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")

if __name__ == "__main__":
    main()