"""
Vedic Horoscope Generator Component
DRY implementation for integration across the Astrologer app
"""

import swisseph as swe
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import streamlit as st
from datetime import datetime

class VedicHoroscopeGenerator:
    """
    Vedic Horoscope Calculator
    Designed for integration with the main Astrologer application
    """
    
    # Comprehensive planet definitions
    PLANETS = {
        'Sun': {'id': swe.SUN, 'symbol': '☉', 'color': '#FFA500'},
        'Moon': {'id': swe.MOON, 'symbol': '☽', 'color': '#C0C0C0'},
        'Mercury': {'id': swe.MERCURY, 'symbol': '☿', 'color': '#32CD32'},
        'Venus': {'id': swe.VENUS, 'symbol': '♀', 'color': '#FF69B4'},
        'Mars': {'id': swe.MARS, 'symbol': '♂', 'color': '#DC143C'},
        'Jupiter': {'id': swe.JUPITER, 'symbol': '♃', 'color': '#DAA520'},
        'Saturn': {'id': swe.SATURN, 'symbol': '♄', 'color': '#8A2BE2'},
        'Rahu': {'id': swe.MEAN_NODE, 'symbol': '☊', 'color': '#1E90FF'},
        'Ketu': {'id': -1, 'symbol': '☋', 'color': '#B22222'}  # Special case
    }
    
    SIGNS = [
        {'name': 'Aries', 'symbol': '♈', 'element': 'Fire', 'quality': 'Cardinal'},
        {'name': 'Taurus', 'symbol': '♉', 'element': 'Earth', 'quality': 'Fixed'},
        {'name': 'Gemini', 'symbol': '♊', 'element': 'Air', 'quality': 'Mutable'},
        {'name': 'Cancer', 'symbol': '♋', 'element': 'Water', 'quality': 'Cardinal'},
        {'name': 'Leo', 'symbol': '♌', 'element': 'Fire', 'quality': 'Fixed'},
        {'name': 'Virgo', 'symbol': '♍', 'element': 'Earth', 'quality': 'Mutable'},
        {'name': 'Libra', 'symbol': '♎', 'element': 'Air', 'quality': 'Cardinal'},
        {'name': 'Scorpio', 'symbol': '♏', 'element': 'Water', 'quality': 'Fixed'},
        {'name': 'Sagittarius', 'symbol': '♐', 'element': 'Fire', 'quality': 'Mutable'},
        {'name': 'Capricorn', 'symbol': '♑', 'element': 'Earth', 'quality': 'Cardinal'},
        {'name': 'Aquarius', 'symbol': '♒', 'element': 'Air', 'quality': 'Fixed'},
        {'name': 'Pisces', 'symbol': '♓', 'element': 'Water', 'quality': 'Mutable'}
    ]
    
    HOUSE_POSITIONS_NORTH = [
        (0, 0.75), (0.75, 0.75), (0.75, 0), (0.75, -0.75),
        (0, -0.75), (-0.75, -0.75), (-0.75, 0), (-0.75, 0.75),
        (-0.375, 0.375), (0.375, 0.375), (0.375, -0.375), (-0.375, -0.375)
    ]

    def __init__(self):
        """Initialize Vedic Horoscope generator with error handling"""
        try:
            swe.set_ephe_path('')
            self.initialized = True
        except Exception as e:
            st.error(f"Failed to initialize Vedic Horoscope generator: {e}")
            self.initialized = False

    def is_ready(self):
        """Check if the calculator is ready to use"""
        return self.initialized

    def calculate_julian_day_with_timezone(self, year, month, day, hour, minute=0, timezone_offset=0):
        """
        Calculate Julian Day with timezone support
        timezone_offset: hours from UTC (e.g., +5.5 for IST)
        """
        # Convert to UTC
        utc_hour = hour - timezone_offset
        if utc_hour < 0:
            utc_hour += 24
            day -= 1
        elif utc_hour >= 24:
            utc_hour -= 24
            day += 1
            
        decimal_hour = utc_hour + (minute / 60.0)
        return swe.julday(year, month, day, decimal_hour)

    def calculate_comprehensive_positions(self, jd):
        """Calculate all planetary positions with detailed information"""
        if not self.initialized:
            return None
            
        positions = {}
        
        for planet_name, planet_data in self.PLANETS.items():
            if planet_name == 'Ketu':
                # Handle Ketu separately
                continue
                
            try:
                result = swe.calc_ut(jd, planet_data['id'])
                longitude = result[0][0]
                latitude = result[0][1]
                distance = result[0][2]
                speed = result[0][3]
                
                sign_index = int(longitude // 30)
                degree_in_sign = longitude % 30
                
                positions[planet_name] = {
                    'longitude': longitude,
                    'latitude': latitude,
                    'distance': distance,
                    'speed': speed,
                    'sign_index': sign_index,
                    'sign_name': self.SIGNS[sign_index]['name'],
                    'sign_symbol': self.SIGNS[sign_index]['symbol'],
                    'degree_in_sign': degree_in_sign,
                    'planet_symbol': planet_data['symbol'],
                    'color': planet_data['color'],
                    'retrograde': speed < 0
                }
                
            except Exception as e:
                st.warning(f"Could not calculate {planet_name}: {e}")
        
        # Calculate Ketu (opposite to Rahu)
        if 'Rahu' in positions:
            rahu_long = positions['Rahu']['longitude']
            ketu_long = (rahu_long + 180.0) % 360.0
            ketu_sign_index = int(ketu_long // 30)
            
            positions['Ketu'] = {
                'longitude': ketu_long,
                'latitude': 0,  # Nodes have no latitude
                'distance': positions['Rahu']['distance'],
                'speed': -positions['Rahu']['speed'],  # Opposite movement
                'sign_index': ketu_sign_index,
                'sign_name': self.SIGNS[ketu_sign_index]['name'],
                'sign_symbol': self.SIGNS[ketu_sign_index]['symbol'],
                'degree_in_sign': ketu_long % 30,
                'planet_symbol': self.PLANETS['Ketu']['symbol'],
                'color': self.PLANETS['Ketu']['color'],
                'retrograde': True  # Nodes are always retrograde
            }
        
        return positions

    def create_enhanced_north_chart(self, positions, chart_title="Vedic Horoscope Chart"):
        """Create enhanced North Indian chart with symbols and colors"""
        fig, ax = plt.subplots(1, 1, figsize=(12, 12))
        ax.set_xlim(-2.2, 2.2)
        ax.set_ylim(-2.2, 2.2)
        ax.set_aspect('equal')
        ax.axis('off')
        
        # Enhanced diamond with gradient effect
        diamond_coords = [(0, 1.8), (1.8, 0), (0, -1.8), (-1.8, 0)]
        diamond = patches.Polygon(diamond_coords, linewidth=3, 
                                 edgecolor='#2E4A8B', facecolor='#F0F8FF', alpha=0.9)
        ax.add_patch(diamond)
        
        # Enhanced internal lines
        ax.plot([0, 0], [-1.8, 1.8], color='#2E4A8B', linewidth=2)
        ax.plot([-1.8, 1.8], [0, 0], color='#2E4A8B', linewidth=2)
        ax.plot([-1.8, 1.8], [-1.8, 1.8], color='#2E4A8B', linewidth=1.5)
        ax.plot([-1.8, 1.8], [1.8, -1.8], color='#2E4A8B', linewidth=1.5)
        
        # Group planets by houses
        houses_with_planets = self._group_by_houses_enhanced(positions)
        
        # Draw houses with enhanced styling
        for i, (x, y) in enumerate(self.HOUSE_POSITIONS_NORTH):
            house_num = i + 1
            
            # Scale positions for larger diamond
            x_scaled, y_scaled = x * 1.2, y * 1.2
            
            # House number with background
            ax.text(x_scaled, y_scaled + 0.2, str(house_num), 
                   ha='center', va='center', fontsize=14, fontweight='bold', 
                   color='white', bbox=dict(boxstyle="circle,pad=0.3", 
                   facecolor='#2E4A8B', alpha=0.8))
            
            # Planets in house with symbols and colors
            if house_num in houses_with_planets:
                self._draw_enhanced_planets(ax, x_scaled, y_scaled - 0.25, 
                                          houses_with_planets[house_num])
        
        # Enhanced title
        ax.text(0, 2.1, chart_title, ha='center', va='center',
               fontsize=18, fontweight='bold', color='#2E4A8B')
        
        plt.tight_layout()
        return fig

    def _group_by_houses_enhanced(self, positions):
        """Enhanced house grouping with planetary data"""
        houses_with_planets = {}
        
        for planet_name, data in positions.items():
            # Simplified house calculation (can be made more accurate)
            house = ((data['sign_index'] + 1) % 12) + 1
            
            if house not in houses_with_planets:
                houses_with_planets[house] = []
                
            planet_info = {
                'name': planet_name,
                'symbol': data['planet_symbol'],
                'color': data['color'],
                'retrograde': data.get('retrograde', False)
            }
            houses_with_planets[house].append(planet_info)
        
        return houses_with_planets

    def _draw_enhanced_planets(self, ax, x, y, planets_list):
        """Draw planets with symbols and colors"""
        if len(planets_list) == 1:
            planet = planets_list[0]
            symbol = f"{planet['symbol']}{'℞' if planet['retrograde'] else ''}"
            ax.text(x, y, symbol, ha='center', va='center',
                   fontsize=16, color=planet['color'], fontweight='bold')
        else:
            # Multiple planets - arrange in a small grid
            cols = 2 if len(planets_list) <= 4 else 3
            for i, planet in enumerate(planets_list):
                row = i // cols
                col = i % cols
                offset_x = (col - (cols-1)/2) * 0.15
                offset_y = (row - 0.5) * 0.1
                
                symbol = f"{planet['symbol']}{'℞' if planet['retrograde'] else ''}"
                ax.text(x + offset_x, y + offset_y, symbol, 
                       ha='center', va='center', fontsize=12, 
                       color=planet['color'], fontweight='bold')

    def create_detailed_report(self, positions):
        """Create detailed planetary report for Streamlit"""
        if not positions:
            return None
            
        report_data = []
        for planet_name, data in positions.items():
            report_data.append({
                'Planet': f"{data['planet_symbol']} {planet_name}",
                'Sign': f"{data['sign_symbol']} {data['sign_name']}",
                'Degree': f"{data['degree_in_sign']:.2f}°",
                'Longitude': f"{data['longitude']:.4f}°",
                'Status': '℞ Retrograde' if data.get('retrograde') else 'Direct',
                'Speed': f"{data.get('speed', 0):.4f}°/day"
            })
        
        return report_data

    def get_quick_summary(self, positions):
        """Get a quick summary for dashboard display"""
        if not positions:
            return "No data available"
            
        summary = {
            'total_planets': len(positions),
            'retrograde_count': sum(1 for p in positions.values() if p.get('retrograde', False)),
            'signs_occupied': len(set(p['sign_name'] for p in positions.values())),
            'dominant_element': self._get_dominant_element(positions)
        }
        
        return summary

    def _get_dominant_element(self, positions):
        """Calculate dominant element from planetary positions"""
        elements = {}
        for planet_data in positions.values():
            sign_index = planet_data['sign_index']
            element = self.SIGNS[sign_index]['element']
            elements[element] = elements.get(element, 0) + 1
        
        return max(elements.items(), key=lambda x: x[1])[0] if elements else 'Unknown'

def create_kundali_widget(birth_data=None):
    """
    Create a Vedic Horoscope widget for use in other pages
    Can be called from any page with birth data
    """
    if birth_data is None:
        st.info("📊 Enter birth details to generate Vedic Horoscope chart")
        return None
    
    calculator = VedicHoroscopeGenerator()
    if not calculator.is_ready():
        st.error("Vedic Horoscope generator not available")
        return None
    
    with st.spinner("Calculating planetary positions..."):
        # Extract birth data
        year = birth_data.get('year', 1990)
        month = birth_data.get('month', 1)
        day = birth_data.get('day', 1)
        hour = birth_data.get('hour', 12)
        minute = birth_data.get('minute', 0)
        
        # Calculate positions
        jd = calculator.calculate_julian_day_with_timezone(year, month, day, hour, minute)
        positions = calculator.calculate_comprehensive_positions(jd)
        
        if positions:
            # Display chart
            chart_title = f"Vedic Horoscope Chart\\n{day}/{month}/{year}"
            fig = calculator.create_enhanced_north_chart(positions, chart_title)
            st.pyplot(fig)
            
            # Quick summary
            summary = calculator.get_quick_summary(positions)
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Planets", summary['total_planets'])
            with col2:
                st.metric("Retrograde", summary['retrograde_count'])
            with col3:
                st.metric("Signs Occupied", summary['signs_occupied'])
            with col4:
                st.metric("Dominant Element", summary['dominant_element'])
            
            return positions
    
    return None
