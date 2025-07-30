# Dasha period calculations
import streamlit as st
from datetime import datetime, timedelta
import swisseph as swe

class VimshottariDashaCalculator:
    """Vimshottari Dasha System Calculator"""
    
    # Vimshottari Dasha periods (in years)
    DASHA_PERIODS = {
        'Sun': 6,
        'Moon': 10,
        'Mars': 7,
        'Rahu': 18,
        'Jupiter': 16,
        'Saturn': 19,
        'Mercury': 17,
        'Ketu': 7,
        'Venus': 20
    }
    
    # Nakshatra to ruling planet mapping
    NAKSHATRA_LORDS = [
        'Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury',  # 1-9
        'Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury',  # 10-18
        'Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury'   # 19-27
    ]
    
    def __init__(self):
        swe.set_ephe_path('')
    
    def calculate_moon_nakshatra(self, birth_date, birth_time):
        """Calculate Moon's nakshatra at birth"""
        try:
            # Convert to Julian Day
            jd = swe.julday(
                birth_date.year, 
                birth_date.month, 
                birth_date.day, 
                birth_time.hour + birth_time.minute/60.0
            )
            
            # Calculate Moon position
            result = swe.calc_ut(jd, swe.MOON)
            moon_longitude = result[0][0]
            
            # Calculate nakshatra (each nakshatra is 13°20' = 13.333...)
            nakshatra_number = int(moon_longitude / 13.333333333) + 1
            nakshatra_degree = moon_longitude % 13.333333333
            
            return {
                'nakshatra_number': nakshatra_number,
                'nakshatra_degree': nakshatra_degree,
                'moon_longitude': moon_longitude,
                'nakshatra_lord': self.NAKSHATRA_LORDS[nakshatra_number - 1]
            }
            
        except Exception as e:
            st.error(f"Error calculating nakshatra: {e}")
            return None
    
    def calculate_dasha_start_date(self, birth_date, birth_time):
        """Calculate when current dasha started"""
        nakshatra_data = self.calculate_moon_nakshatra(birth_date, birth_time)
        if not nakshatra_data:
            return None
        
        # Calculate how much of the nakshatra is completed
        nakshatra_completed = nakshatra_data['nakshatra_degree'] / 13.333333333
        
        # Get the ruling planet and its period
        ruling_planet = nakshatra_data['nakshatra_lord']
        total_period_years = self.DASHA_PERIODS[ruling_planet]
        
        # Calculate remaining period at birth
        remaining_years = total_period_years * (1 - nakshatra_completed)
        
        # Calculate when this dasha started (before birth)
        completed_years = total_period_years - remaining_years
        birth_datetime = datetime.combine(birth_date, birth_time)
        dasha_start_date = birth_datetime - timedelta(days=completed_years * 365.25)
        
        return {
            'ruling_planet': ruling_planet,
            'dasha_start_date': dasha_start_date,
            'total_period_years': total_period_years,
            'completed_at_birth_years': completed_years,
            'remaining_at_birth_years': remaining_years,
            'nakshatra_data': nakshatra_data
        }
    
    def get_current_dasha(self, birth_date, birth_time):
        """Get current running dasha"""
        dasha_info = self.calculate_dasha_start_date(birth_date, birth_time)
        if not dasha_info:
            return None
        
        current_date = datetime.now()
        birth_datetime = datetime.combine(birth_date, birth_time)
        
        # Calculate time elapsed since birth
        elapsed_time = current_date - birth_datetime
        elapsed_years = elapsed_time.days / 365.25
        
        # Start with the birth dasha information
        current_planet = dasha_info['ruling_planet']
        current_start = dasha_info['dasha_start_date']
        remaining_at_birth = dasha_info['remaining_at_birth_years']
        
        # If we haven't completed the birth dasha yet
        if elapsed_years <= remaining_at_birth:
            remaining_years = remaining_at_birth - elapsed_years
            return {
                'current_planet': current_planet,
                'dasha_start_date': current_start,
                'total_period_years': self.DASHA_PERIODS[current_planet],
                'elapsed_years': self.DASHA_PERIODS[current_planet] - remaining_years,
                'remaining_years': remaining_years,
                'end_date': birth_datetime + timedelta(days=remaining_at_birth * 365.25)
            }
        
        # Move through subsequent dashas
        years_to_account = elapsed_years - remaining_at_birth
        current_start = birth_datetime + timedelta(days=remaining_at_birth * 365.25)
        
        # Get dasha sequence starting from next planet
        planet_sequence = list(self.DASHA_PERIODS.keys())
        start_index = (planet_sequence.index(current_planet) + 1) % len(planet_sequence)
        
        while years_to_account > 0:
            current_planet = planet_sequence[start_index]
            period_years = self.DASHA_PERIODS[current_planet]
            
            if years_to_account <= period_years:
                # Current dasha found
                remaining_years = period_years - years_to_account
                return {
                    'current_planet': current_planet,
                    'dasha_start_date': current_start,
                    'total_period_years': period_years,
                    'elapsed_years': years_to_account,
                    'remaining_years': remaining_years,
                    'end_date': current_start + timedelta(days=period_years * 365.25)
                }
            
            # Move to next dasha
            years_to_account -= period_years
            current_start += timedelta(days=period_years * 365.25)
            start_index = (start_index + 1) % len(planet_sequence)
        
        return None
    
    def get_complete_life_dasha_timeline(self, birth_date, birth_time):
        """Get complete dasha timeline from birth to 100 years"""
        dasha_info = self.calculate_dasha_start_date(birth_date, birth_time)
        if not dasha_info:
            return None
        
        timeline = []
        birth_datetime = datetime.combine(birth_date, birth_time)
        end_of_life = birth_datetime + timedelta(days=100 * 365.25)  # 100 years from birth
        current_date = datetime.now()
        
        # Start from the birth dasha
        current_planet = dasha_info['ruling_planet']
        current_start = dasha_info['dasha_start_date']
        remaining_at_birth = dasha_info['remaining_at_birth_years']
        
        # First period - the one active at birth
        first_end = birth_datetime + timedelta(days=remaining_at_birth * 365.25)
        
        # Check if this period is current, past, or future
        is_current = current_start <= current_date < first_end
        is_past = first_end <= current_date
        
        if is_current:
            elapsed_since_start = (current_date - current_start).days / 365.25
            elapsed_since_birth = (current_date - birth_datetime).days / 365.25
            remaining = remaining_at_birth - elapsed_since_birth
            
            timeline.append({
                'planet': current_planet,
                'start_date': current_start,
                'end_date': first_end,
                'is_current': True,
                'is_past': False,
                'elapsed_years': elapsed_since_start,
                'remaining_years': remaining,
                'period_years': self.DASHA_PERIODS[current_planet]
            })
        else:
            timeline.append({
                'planet': current_planet,
                'start_date': current_start,
                'end_date': first_end,
                'is_current': False,
                'is_past': is_past,
                'period_years': self.DASHA_PERIODS[current_planet]
            })
        
        # Continue with subsequent dashas until 100 years
        current_start_date = first_end
        planet_sequence = list(self.DASHA_PERIODS.keys())
        current_index = planet_sequence.index(current_planet)
        
        while current_start_date < end_of_life:
            current_index = (current_index + 1) % len(planet_sequence)
            planet = planet_sequence[current_index]
            period_years = self.DASHA_PERIODS[planet]
            end_date = current_start_date + timedelta(days=period_years * 365.25)
            
            # Check status relative to current date
            is_current = current_start_date <= current_date < end_date
            is_past = end_date <= current_date
            
            period_data = {
                'planet': planet,
                'start_date': current_start_date,
                'end_date': end_date,
                'is_current': is_current,
                'is_past': is_past,
                'period_years': period_years
            }
            
            # Add elapsed/remaining for current period
            if is_current:
                elapsed_years = (current_date - current_start_date).days / 365.25
                remaining_years = period_years - elapsed_years
                period_data.update({
                    'elapsed_years': elapsed_years,
                    'remaining_years': remaining_years
                })
            
            timeline.append(period_data)
            current_start_date = end_date
        
        return timeline
