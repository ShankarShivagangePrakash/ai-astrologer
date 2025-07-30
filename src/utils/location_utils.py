"""
Location utilities for geocoding and coordinate management
Provides functions to fetch latitude and longitude from city, state, country inputs
"""

import streamlit as st
import requests
from typing import Dict, Optional, Tuple
import time
from src.utils.common import render_error_messages

class LocationService:
    """Service to handle location-based operations"""
    
    def __init__(self):
        self.cache = {}
        
    def get_coordinates_from_location(self, city: str, state: str, country: str) -> Optional[Dict]:
        """
        Get latitude and longitude from city, state, country
        Uses OpenStreetMap Nominatim API (free, no API key required)
        """
        # Create cache key
        cache_key = f"{city.lower()}, {state.lower()}, {country.lower()}"
        
        # Check cache first
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Build query string
        query_parts = []
        if city.strip():
            query_parts.append(city.strip())
        if state.strip():
            query_parts.append(state.strip())
        if country.strip():
            query_parts.append(country.strip())
            
        if not query_parts:
            return None
            
        query = ", ".join(query_parts)
        
        try:
            # Use Nominatim API (free OpenStreetMap service)
            url = "https://nominatim.openstreetmap.org/search"
            params = {
                'q': query,
                'format': 'json',
                'limit': 1,
                'addressdetails': 1
            }
            
            headers = {
                'User-Agent': 'AstrologerApp/1.0 (vedic-astrology-app)'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data and len(data) > 0:
                result = data[0]
                location_data = {
                    'latitude': float(result['lat']),
                    'longitude': float(result['lon']),
                    'display_name': result.get('display_name', query),
                    'formatted_address': self._format_address(result.get('address', {})),
                    'query': query
                }
                
                # Cache the result
                self.cache[cache_key] = location_data
                return location_data
            else:
                st.warning(f"⚠️ Location not found: {query}")
                return None
                
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Network error while fetching location: {str(e)}")
            return None
        except Exception as e:
            st.error(f"❌ Error fetching coordinates: {str(e)}")
            return None
    
    def _format_address(self, address_components: Dict) -> str:
        """Format address from Nominatim response"""
        parts = []
        
        # Add city/town/village
        for key in ['city', 'town', 'village', 'hamlet']:
            if key in address_components:
                parts.append(address_components[key])
                break
        
        # Add state/region
        for key in ['state', 'region', 'province']:
            if key in address_components:
                parts.append(address_components[key])
                break
        
        # Add country
        if 'country' in address_components:
            parts.append(address_components['country'])
            
        return ", ".join(parts) if parts else "Unknown"
    
    def validate_location_inputs(self, city: str, state: str, country: str) -> list:
        """Validate location input fields"""
        errors = []
        
        # At least city and country should be provided
        if not city or len(city.strip()) < 2:
            errors.append("City is required (minimum 2 characters)")
            
        if not country or len(country.strip()) < 2:
            errors.append("Country is required (minimum 2 characters)")
            
        # State is optional but if provided, should be valid
        if state and len(state.strip()) < 2:
            errors.append("State should be at least 2 characters if provided")
            
        return errors
    
    def get_timezone_offset(self, latitude: float, longitude: float) -> float:
        """
        Get approximate timezone offset based on longitude
        This is a simple approximation - for production, use a proper timezone service
        """
        # Simple approximation: 15 degrees longitude = 1 hour
        # This is not accurate for all locations but provides a basic estimate
        offset = longitude / 15.0
        return round(offset * 2) / 2  # Round to nearest half hour

# Global instance
location_service = LocationService()

def render_location_inputs(default_city="", default_state="", default_country=""):
    """
    Render location input fields (city, state, country)
    Returns: tuple of (city, state, country)
    """
    st.write("**Birth Location:**")
    
    # Create three columns for location inputs
    loc_col1, loc_col2, loc_col3 = st.columns([2, 2, 2])
    
    with loc_col1:
        city = st.text_input(
            "City*", 
            value=default_city,
            placeholder="e.g., Mumbai, New York",
            help="Enter the city where you were born"
        )
    
    with loc_col2:
        state = st.text_input(
            "State/Province", 
            value=default_state,
            placeholder="e.g., Maharashtra, New York",
            help="Enter state or province (optional but recommended)"
        )
    
    with loc_col3:
        country = st.text_input(
            "Country*", 
            value=default_country,
            placeholder="e.g., India, USA",
            help="Enter the country where you were born"
        )
    
    return city, state, country

def fetch_coordinates_for_location(city: str, state: str, country: str) -> Optional[Dict]:
    """
    Fetch coordinates for given location without UI interaction
    Returns coordinates dictionary or None if not found
    """
    if not city or not country:
        return None
        
    return location_service.get_coordinates_from_location(city, state, country)

def create_location_data_dict(city: str, state: str, country: str, coordinates: Optional[Dict] = None) -> Dict:
    """Create standardized location data dictionary"""
    location_data = {
        'city': city.strip() if city else '',
        'state': state.strip() if state else '',
        'country': country.strip() if country else '',
        'coordinates': coordinates,
        'place_string': f"{city}, {state}, {country}" if state else f"{city}, {country}"
    }
    
    if coordinates:
        location_data.update({
            'latitude': coordinates['latitude'],
            'longitude': coordinates['longitude'],
            'formatted_address': coordinates.get('formatted_address', ''),
            'timezone_offset': location_service.get_timezone_offset(
                coordinates['latitude'], 
                coordinates['longitude']
            )
        })
    
    return location_data

def validate_location_data(location_data: Dict) -> list:
    """Validate location data dictionary - coordinates will be fetched automatically"""
    errors = []
    
    if not location_data.get('city'):
        errors.append("City is required")
    
    if not location_data.get('country'):
        errors.append("Country is required")
    
    # Note: We don't require coordinates here anymore as they'll be fetched automatically
    
    return errors

def get_location_summary(location_data: Dict) -> str:
    """Get formatted summary of location data"""
    if not location_data:
        return "No location data"
    
    city = location_data.get('city', '')
    state = location_data.get('state', '')
    country = location_data.get('country', '')
    
    if coordinates := location_data.get('coordinates'):
        coord_str = f" ({coordinates['latitude']:.2f}°, {coordinates['longitude']:.2f}°)"
    else:
        coord_str = " (coordinates not fetched)"
    
    place_str = f"{city}, {state}, {country}" if state else f"{city}, {country}"
    return f"📍 {place_str}{coord_str}"
