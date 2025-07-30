"""
Vedic Horoscope Generator - Streamlit Integration
Direct implementation using pyswisseph for Vedic astrology
Now with DRY principles and integrated design
"""

import streamlit as st
import swisseph as swe
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from datetime import datetime
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import page utilities and navigation
from src.utils.page_utils import setup_page, render_page_header
from src.utils.ui_components import render_sidebar_navigation

# Import cleanup utility
try:
    from utils.cleanup import auto_cleanup, register_for_cleanup
    CLEANUP_AVAILABLE = True
except ImportError:
    CLEANUP_AVAILABLE = False
    def auto_cleanup():
        pass
    def register_for_cleanup(filepath):
        pass

class StreamlitVedicHoroscopeGenerator:
    """Vedic Horoscope Calculator using DRY principles for Streamlit"""
    
    # Class constants - defined once
    PLANETS = {
        'Sun': {'id': swe.SUN, 'abbrev': 'Su', 'color': 'orange'},
        'Moon': {'id': swe.MOON, 'abbrev': 'Mo', 'color': 'silver'},
        'Mercury': {'id': swe.MERCURY, 'abbrev': 'Me', 'color': 'green'},
        'Venus': {'id': swe.VENUS, 'abbrev': 'Ve', 'color': 'pink'},
        'Mars': {'id': swe.MARS, 'abbrev': 'Ma', 'color': 'red'},
        'Jupiter': {'id': swe.JUPITER, 'abbrev': 'Ju', 'color': 'gold'},
        'Saturn': {'id': swe.SATURN, 'abbrev': 'Sa', 'color': 'purple'},
        'Rahu': {'id': swe.MEAN_NODE, 'abbrev': 'Ra', 'color': 'darkblue'}
    }
    
    SIGN_NAMES = [
        'Aries', 'Taurus', 'Gemini', 'Cancer',
        'Leo', 'Virgo', 'Libra', 'Scorpio', 
        'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
    ]
    
    # Chart layout constants
    CHART_SIZE = 10
    DIAMOND_SIZE = 1.5
    HOUSE_POSITIONS = [
        (0, 0.75),      # House 1 (Ascendant)
        (0.75, 0.75),   # House 2
        (0.75, 0),      # House 3
        (0.75, -0.75),  # House 4
        (0, -0.75),     # House 5
        (-0.75, -0.75), # House 6
        (-0.75, 0),     # House 7
        (-0.75, 0.75),  # House 8
        (-0.375, 0.375), # House 9
        (0.375, 0.375),  # House 10
        (0.375, -0.375), # House 11
        (-0.375, -0.375) # House 12
    ]

    def __init__(self):
        """Initialize Vedic Horoscope generator"""
        swe.set_ephe_path('')

    def calculate_julian_day(self, year, month, day, hour):
        """Calculate Julian Day - extracted for reusability"""
        return swe.julday(year, month, day, hour)

    def calculate_planet_position(self, jd, planet_name, planet_id):
        """Calculate single planet position - DRY for planet calculations"""
        try:
            result = swe.calc_ut(jd, planet_id)
            longitude = result[0][0]
            
            return {
                'longitude': longitude,
                'sign': int(longitude // 30),
                'degree': longitude % 30
            }
        except Exception as e:
            st.error(f"Error calculating {planet_name}: {e}")
            return None

    def calculate_all_positions(self, jd):
        """Calculate all planetary positions - DRY for position calculations"""
        positions = {}
        
        # Calculate main planets
        for planet_name, planet_data in self.PLANETS.items():
            position = self.calculate_planet_position(jd, planet_name, planet_data['id'])
            if position:
                positions[planet_name] = {
                    **position,
                    'abbrev': planet_data['abbrev'],
                    'color': planet_data['color']
                }
        
        # Add Ketu (opposite to Rahu)
        if 'Rahu' in positions:
            ketu_longitude = (positions['Rahu']['longitude'] + 180.0) % 360.0
            positions['Ketu'] = {
                'longitude': ketu_longitude,
                'sign': int(ketu_longitude // 30),
                'degree': ketu_longitude % 30,
                'abbrev': 'Ke',
                'color': 'darkred'
            }
        
        return positions

    def group_planets_by_houses(self, positions):
        """Group planets by houses - extracted for reusability"""
        houses_with_planets = {}
        for planet, data in positions.items():
            house = ((data['sign'] + 1) % 12) + 1
            if house not in houses_with_planets:
                houses_with_planets[house] = []
            houses_with_planets[house].append(planet)  # Use full planet name
        return houses_with_planets

    def create_chart_figure(self):
        """Create and setup chart figure - DRY for chart setup"""
        fig, ax = plt.subplots(1, 1, figsize=(self.CHART_SIZE, self.CHART_SIZE))
        ax.set_xlim(-2, 2)
        ax.set_ylim(-2, 2)
        ax.set_aspect('equal')
        ax.axis('off')
        return fig, ax

    def draw_diamond_structure(self, ax):
        """Draw diamond structure and internal lines - DRY for chart structure"""
        # Diamond coordinates
        diamond_coords = [(0, self.DIAMOND_SIZE), (self.DIAMOND_SIZE, 0), 
                         (0, -self.DIAMOND_SIZE), (-self.DIAMOND_SIZE, 0)]
        
        # Create diamond
        diamond = patches.Polygon(diamond_coords, linewidth=3, 
                                 edgecolor='black', facecolor='white')
        ax.add_patch(diamond)
        
        # Internal lines
        self._draw_chart_lines(ax)

    def _draw_chart_lines(self, ax):
        """Draw internal chart lines - extracted for clarity"""
        size = self.DIAMOND_SIZE
        ax.plot([0, 0], [-size, size], 'k-', linewidth=2)          # Vertical
        ax.plot([-size, size], [0, 0], 'k-', linewidth=2)          # Horizontal
        ax.plot([-size, size], [-size, size], 'k-', linewidth=2)   # Diagonal /
        ax.plot([-size, size], [size, -size], 'k-', linewidth=2)   # Diagonal 

    def draw_houses_and_planets(self, ax, houses_with_planets):
        """Draw house numbers and planets - DRY for house display"""
        for i, (x, y) in enumerate(self.HOUSE_POSITIONS):
            house_num = i + 1
            self._draw_house_number(ax, x, y, house_num)
            self._draw_planets_in_house(ax, x, y, house_num, houses_with_planets)

    def _draw_house_number(self, ax, x, y, house_num):
        """Draw single house number - extracted for clarity"""
        ax.text(x, y + 0.15, str(house_num), ha='center', va='center',
               fontsize=12, fontweight='bold', color='blue',
               bbox=dict(boxstyle="round,pad=0.3", facecolor='lightblue', alpha=0.7))

    def _draw_planets_in_house(self, ax, x, y, house_num, houses_with_planets):
        """Draw planets in a specific house - extracted for clarity"""
        if house_num in houses_with_planets:
            planets_text = ', '.join(houses_with_planets[house_num])
            ax.text(x, y - 0.15, planets_text, ha='center', va='center',
                   fontsize=9, color='red', fontweight='bold')

    def add_chart_title(self, ax, title):
        """Add title to chart - DRY for chart labeling"""
        ax.text(0, 1.8, title, ha='center', va='center',
               fontsize=16, fontweight='bold')

    def create_north_indian_chart(self, positions, title="Vedic Horoscope Chart"):
        """Create North Indian diamond chart using DRY principles"""
        # Group planets by houses
        houses_with_planets = self.group_planets_by_houses(positions)
        
        # Create chart
        fig, ax = self.create_chart_figure()
        self.draw_diamond_structure(ax)
        self.draw_houses_and_planets(ax, houses_with_planets)
        self.add_chart_title(ax, title)
        
        plt.tight_layout()
        return fig

    def display_planetary_positions(self, positions):
        """Display planetary positions in a table"""
        st.subheader("🪐 Planetary Positions")
        
        data = []
        for planet, pos in positions.items():
            sign_name = self.SIGN_NAMES[pos['sign']]
            data.append({
                'Planet': f"{planet}",
                'Longitude': f"{pos['longitude']:.2f}°",
                'Sign': sign_name,
                'Degree': f"{pos['degree']:.2f}°"
            })
        
        st.table(data)

    def display_houses_summary(self, positions):
        """Display houses with planets summary"""
        st.subheader("🏠 Houses Summary")
        
        houses_with_planets = self.group_planets_by_houses(positions)
        
        cols = st.columns(3)
        for i, house_num in enumerate(sorted(houses_with_planets.keys())):
            col_idx = i % 3
            with cols[col_idx]:
                planets_list = ', '.join(houses_with_planets[house_num])
                st.write(f"**House {house_num}:** {planets_list}")

def render_vedic_horoscope_content(birth_data):
    """Render vedic horoscope generation content using session birth data"""
    # Import the enhanced component
    from components.VedicHoroscopeGenerator import create_kundali_widget, VedicHoroscopeGenerator
    from components.birth_data_display import render_coordinates_status
    
    # Display birth data info with enhanced location display
    st.subheader("📋 Birth Information")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**📅 Date:** {birth_data.get('date', 'Unknown')}")
        
        # Handle enhanced location display
        if isinstance(birth_data.get('location'), dict):
            location_data = birth_data['location']
            city = location_data.get('city', '')
            state = location_data.get('state', '')
            country = location_data.get('country', '')
            place_str = f"{city}, {state}, {country}" if state else f"{city}, {country}"
            st.write(f"**📍 Place:** {place_str}")
            
            if coordinates := location_data.get('coordinates'):
                st.write(f"**🌍 Latitude:** {coordinates['latitude']:.6f}°")
                st.write(f"**🌍 Longitude:** {coordinates['longitude']:.6f}°")
                
                # Show verified address
                if formatted_address := coordinates.get('formatted_address'):
                    st.caption(f"*Verified as: {formatted_address}*")
        else:
            st.write(f"**📍 Place:** {birth_data.get('place', 'Unknown')}")
            st.caption("*⚠️ No coordinates available - using approximate location*")
            
    with col2:
        st.write(f"**⏰ Time:** {birth_data.get('time', 'Unknown')}")
        if birth_data.get('hour') is not None and birth_data.get('minute') is not None:
            st.write(f"**🕐 Precise Time:** {birth_data.get('hour'):02d}:{birth_data.get('minute'):02d}")
            
        # Show timezone information if available
        if birth_data.get('timezone_offset') is not None:
            offset = birth_data['timezone_offset']
            st.write(f"**🌐 Timezone Offset:** {offset:+.1f} hours from UTC")
        else:
            st.write(f"**🌐 Timezone:** Auto-detected from coordinates")
    
    # Show coordinates status
    st.markdown("---")
    render_coordinates_status()
    st.markdown("---")
    
    # Chart options
    st.subheader("🎨 Chart Options")
    option_col1, option_col2, option_col3 = st.columns(3)
    with option_col1:
        show_positions = st.checkbox("Show Planetary Positions", value=True)
    with option_col2:
        show_houses = st.checkbox("Show Houses Summary", value=True)
    with option_col3:
        show_technical = st.checkbox("Show Technical Details", value=False)
    
    # Generate button
    st.markdown("---")
    if st.button("🚀 Generate Vedic Horoscope", type="primary", use_container_width=True):
        # Use the enhanced create_kundali_widget function
        positions = create_kundali_widget(birth_data)
        
        if positions:
            st.markdown("---")
            
            # Additional detailed information if requested
            if show_positions:
                with st.expander("📋 Detailed Planetary Positions", expanded=True):
                    calculator = VedicHoroscopeGenerator()
                    report_data = calculator.create_detailed_report(positions)
                    if report_data:
                        st.dataframe(report_data, use_container_width=True)
            
            if show_houses:
                with st.expander("🏠 Houses Summary", expanded=True):
                    calculator = VedicHoroscopeGenerator()
                    houses_with_planets = calculator._group_by_houses_enhanced(positions)
                    
                    cols = st.columns(3)
                    for i, house_num in enumerate(sorted(houses_with_planets.keys())):
                        col_idx = i % 3
                        with cols[col_idx]:
                            planets_list = [p['name'] for p in houses_with_planets[house_num]]
                            planets_text = ', '.join(planets_list)
                            st.write(f"**House {house_num}:** {planets_text}")
            
            if show_technical:
                with st.expander("🔧 Technical Details", expanded=False):
                    calculator = VedicHoroscopeGenerator()
                    birth_date = birth_data['date']
                    birth_time = birth_data['time']
                    
                    # Show different JD calculations based on available data
                    if birth_data.get('latitude') and birth_data.get('longitude'):
                        jd = calculator.calculate_julian_day_with_coordinates(
                            birth_date.year, birth_date.month, birth_date.day,
                            birth_time.hour, birth_time.minute,
                            birth_data['latitude'], birth_data['longitude']
                        )
                        st.write(f"**Julian Day (coordinates):** {jd:.6f}")
                        st.write(f"**Calculation Method:** Using precise geographical coordinates")
                    else:
                        jd = calculator.calculate_julian_day_with_timezone(
                            birth_date.year, birth_date.month, birth_date.day,
                            birth_time.hour, birth_time.minute
                        )
                        st.write(f"**Julian Day (timezone):** {jd:.6f}")
                        st.write(f"**Calculation Method:** Using timezone approximation")
                    
                    st.write(f"**Total Planets:** {len(positions)}")
                    st.write(f"**Birth Coordinates:** Using session data")
        else:
            st.error("❌ Failed to calculate planetary positions. Please check your birth data.")

def main():
    # Use standard page layout with birth data checking
    page_config = {
        'title': '🔮 Generate Vedic Horoscope',
        'icon': '🔮',
        'subtitle': 'Professional Vedic Birth Chart using Session Data',
        'content_callback': render_vedic_horoscope_content,
        'page_id': 'vedic_horoscope'
    }
    
    from src.utils.page_utils import create_standard_page_layout
    create_standard_page_layout(page_config)

if __name__ == "__main__":
    main()
