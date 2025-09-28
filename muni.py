import os
from google.transit import gtfs_realtime_pb2
import requests
from datetime import datetime
import pytz
from typing import List, Dict, Optional
from dotenv import load_dotenv
import zipfile
from io import BytesIO, TextIOWrapper
import csv

# Load environment variables
load_dotenv()

class MuniAPI:
    def __init__(self):
        self.api_key = os.getenv('TRANSIT_511_API_KEY')
        if not self.api_key:
            raise ValueError("511 Transit API key not found in environment variables")
        
        self.base_url = "http://api.511.org/transit"
        self.agency = "SF"  # San Francisco Muni
        
        # Cache for GTFS data
        self.routes = {}
        self.trips = {}
        self.stops = {}
        
        # Load GTFS data on initialization
        self._load_gtfs_data()
    
    def _load_gtfs_data(self):
        """Load static GTFS data from 511.org"""
        url = f"{self.base_url}/datafeeds"
        params = {
            "api_key": self.api_key,
            "operator_id": self.agency
        }
        
        response = requests.get(url, params=params)
        if not response.ok:
            raise Exception(f"Failed to fetch GTFS data: {response.status_code} - {response.text}")
        
        # Parse the zip file
        with zipfile.ZipFile(BytesIO(response.content)) as z:
            # Load routes
            with z.open('routes.txt') as f:
                reader = csv.DictReader(TextIOWrapper(f))
                for row in reader:
                    self.routes[row['route_id']] = {
                        'route_short_name': row['route_short_name'],
                        'route_long_name': row['route_long_name']
                    }
            
            # Load trips
            with z.open('trips.txt') as f:
                reader = csv.DictReader(TextIOWrapper(f))
                for row in reader:
                    self.trips[row['trip_id']] = {
                        'route_id': row['route_id'],
                        'direction_id': int(row['direction_id']) if 'direction_id' in row else 0,
                        'trip_headsign': row['trip_headsign'] if 'trip_headsign' in row else None
                    }
            
            # Load stops
            with z.open('stops.txt') as f:
                reader = csv.DictReader(TextIOWrapper(f))
                for row in reader:
                    self.stops[row['stop_id']] = {
                        'stop_name': row['stop_name'],
                        'stop_desc': row.get('stop_desc', '')
                    }
    
    def get_trip_info(self, trip_id: str) -> Optional[Dict]:
        """Get trip information including headsign from cache"""
        return self.trips.get(trip_id)

    def get_route_info(self, route_id: str) -> Optional[Dict]:
        """Get route information from cache"""
        return self.routes.get(route_id)

    def get_stop_info(self, stop_id: str) -> Optional[Dict]:
        """Get stop information from cache"""
        return self.stops.get(stop_id)

    def get_trip_updates(self) -> gtfs_realtime_pb2.FeedMessage:
        """Fetch real-time trip updates from 511.org API"""
        url = f"{self.base_url}/tripupdates"
        params = {
            "api_key": self.api_key,
            "agency": self.agency
        }
        
        response = requests.get(url, params=params)
        if not response.ok:
            raise Exception(f"Failed to fetch trip updates: {response.status_code} - {response.text}")
        
        # Parse the protobuf message
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(response.content)
        return feed

    def get_stop_predictions(self, stop_ids: List[str], num_predictions: int = 3) -> Dict[str, List[Dict[str, any]]]:
        """
        Get predictions for multiple stops
        
        Args:
            stop_ids: List of stop IDs to get predictions for
            num_predictions: Number of predictions to return per route/direction (default 3)
            
        Returns:
            Dictionary mapping stop_ids to lists of predictions
        """
        feed = self.get_trip_updates()
        
        # Create a dictionary to store predictions for each stop
        all_predictions = {stop_id: [] for stop_id in stop_ids}
        
        # Process trip updates to find predictions for our stops
        for entity in feed.entity:
            if entity.HasField('trip_update'):
                trip_update = entity.trip_update
                trip = trip_update.trip
                
                # Look through stop time updates
                for stop_time_update in trip_update.stop_time_update:
                    stop_id = stop_time_update.stop_id
                    if stop_id in stop_ids:
                        # Get arrival time if available
                        if stop_time_update.HasField('arrival'):
                            arrival_time = datetime.fromtimestamp(
                                stop_time_update.arrival.time,
                                pytz.timezone('America/Los_Angeles')
                            )
                            
                            # Get trip info from GTFS data
                            trip_info = self.get_trip_info(trip.trip_id)
                            route_info = self.get_route_info(trip.route_id)
                            
                            all_predictions[stop_id].append({
                                'route_id': trip.route_id,
                                'route_name': route_info.get('route_long_name', '') if route_info else '',
                                'trip_id': trip.trip_id,
                                'direction_id': trip.direction_id if trip.HasField('direction_id') else 0,
                                'headsign': trip_info.get('trip_headsign', '') if trip_info else '',
                                'arrival_time': arrival_time
                            })
        
        # For each stop, group predictions by route and direction
        processed_predictions = {}
        for stop_id, predictions in all_predictions.items():
            # Sort all predictions by arrival time
            predictions.sort(key=lambda x: x['arrival_time'])
            
            # Group by route and direction
            route_groups = {}
            for pred in predictions:
                route_id = pred['route_id']
                direction = pred['headsign']
                if not direction:  # Fallback if no headsign available
                    direction = "Inbound" if pred['direction_id'] == 0 else "Outbound"
                key = (route_id, direction)
                
                if key not in route_groups:
                    route_groups[key] = []
                
                if len(route_groups[key]) < num_predictions:
                    route_groups[key].append(pred)
            
            processed_predictions[stop_id] = route_groups
        
        return processed_predictions

    def format_predictions(self, predictions_by_stop: Dict[str, Dict[tuple, List[Dict[str, any]]]], show_stop_ids: bool = True) -> str:
        """Format predictions into a human-readable string"""
        if not predictions_by_stop:
            return "No predictions available"
            
        now = datetime.now(pytz.timezone('America/Los_Angeles'))
        all_results = []
        
        for stop_id, route_groups in predictions_by_stop.items():
            if show_stop_ids:
                all_results.append(f"\nStop {stop_id}:")
            
            if not route_groups:
                all_results.append("  No predictions available")
                continue
                
            # Sort routes numerically
            sorted_groups = sorted(route_groups.items(), key=lambda x: int(x[0][0]) if x[0][0].isdigit() else float('inf'))
            
            for (route_id, direction), preds in sorted_groups:
                # Format times
                times = []
                for pred in preds:
                    minutes = int((pred['arrival_time'] - now).total_seconds() / 60)
                    if minutes <= 0:
                        times.append("Arriving")
                    else:
                        times.append(f"{minutes} min")
                
                # Add the route line
                times_str = ", ".join(times)
                all_results.append(f"  {route_id} ({direction}): {times_str}")
            
        return "\n".join(all_results)

def main():
    # Initialize API
    muni = MuniAPI()
    
    # Example stop IDs - this should be configured in main.py
    stop_ids = ["18092", "18101", "16303", "14022", "13812", "16597", "16016", "15813", "14302"]  # Example stop IDs
    
    try:
        predictions = muni.get_stop_predictions(stop_ids)
        print("\nMuni Predictions:")
        print(muni.format_predictions(predictions))
    except Exception as e:
        print(f"Error getting predictions: {e}")

if __name__ == "__main__":
    main()
