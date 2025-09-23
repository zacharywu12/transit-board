from bike import get_station_bike_availability
from typing import Dict
import time
import os
from datetime import datetime

target_stations_shortnames = ["SF-F23-2", "SF-F23-3", "SF-F23", "SF-F24", "SF-G24"]

def format_table(stations: Dict[str, dict]) -> str:
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
    try:
        while True:
            try:
                clear_screen()
                stations = get_station_bike_availability(target_stations_shortnames)
                print(f"\nLast updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} PST")
                print("\n" + format_table(stations) + "\n")
                time.sleep(30)
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(5)  # Wait a bit before retrying if there's an error
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")

if __name__ == "__main__":
    main()