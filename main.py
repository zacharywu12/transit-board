from bike import get_station_bike_availability
from typing import Dict

target_stations_shortnames = ["SF-F23-2", "SF-F23-3", "SF-F23", "SF-F24", "SF-G24"]

def print_station_info(stations: Dict[str, dict]) -> None:
    """
    Print formatted bike availability information for each station.
    
    Args:
        stations: Dictionary of station information from get_station_bike_availability
    """
    for shortname, info in stations.items():
        print(f"\nStation: {info['name']}")
        print(f"Regular bikes available: {info['bikes_available']}")
        print(f"E-bikes available: {info['ebikes_available']}")

def main():
    try:
        stations = get_station_bike_availability(target_stations_shortnames)
        print_station_info(stations)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()