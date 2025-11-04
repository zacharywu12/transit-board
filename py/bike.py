
import requests
from typing import List, Dict

station_info_url = "https://gbfs.lyft.com/gbfs/2.3/bay/en/station_information.json"
station_status_url = "https://gbfs.lyft.com/gbfs/2.3/bay/en/station_status.json"

def get_station_bike_availability(station_shortnames: List[str]) -> Dict[str, dict]:
    """
    Fetches and returns bike availability information for specified stations.
    
    Args:
        station_shortnames: List of station short names to look up
        
    Returns:
        Dictionary mapping station shortnames to their availability info:
        {
            'station_shortname': {
                'name': str,
                'bikes_available': int,
                'ebikes_available': int,
            }
        }
    """
    # Fetch station information and status
    info_response = requests.get(station_info_url)
    status_response = requests.get(station_status_url)
    
    if not info_response.ok or not status_response.ok:
        raise Exception("Failed to fetch station data")

    station_info = info_response.json()
    station_status = status_response.json()

    # Process only the requested stations
    results = {}
    all_stations = station_info['data']['stations']
    all_status = {s['station_id']: s for s in station_status['data']['stations']}

    for shortname in station_shortnames:
        # Find the station with matching shortname
        station = next((s for s in all_stations if s.get('short_name') == shortname), None)
        if not station:
            raise ValueError(f"Station with shortname '{shortname}' not found")
        
        # Get the status for this station
        station_id = station['station_id']
        status = all_status.get(station_id)
        if not status:
            raise ValueError(f"Status not found for station '{shortname}'")
        
        # Add to results        
        results[shortname] = {
            'name': station['name'],
            'bikes_available': status['num_bikes_available'] - status['num_ebikes_available'],
            'ebikes_available': status['num_ebikes_available'],
        }
    
    return results
