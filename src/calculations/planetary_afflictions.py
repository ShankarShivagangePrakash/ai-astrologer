"""
Planetary Afflictions Calculator for Vedic Astrology
Calculates major afflictions like Sade Sathi, Kuja Dosha, etc. from birth to 100 years
"""

import swisseph as swe
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import math

class PlanetaryAfflictionsCalculator:
    def __init__(self):
        """Initialize the planetary afflictions calculator"""
        # Set ephemeris path
        swe.set_ephe_path('')
        
        # Planet constants
        self.PLANETS = {
            'sun': swe.SUN,
            'moon': swe.MOON,
            'mars': swe.MARS,
            'mercury': swe.MERCURY,
            'jupiter': swe.JUPITER,
            'venus': swe.VENUS,
            'saturn': swe.SATURN,
            'rahu': swe.MEAN_NODE,
            'ketu': swe.MEAN_NODE  # Ketu is 180° opposite to Rahu
        }
        
        # Nakshatras for Sade Sathi calculation
        self.NAKSHATRAS = [
            "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu",
            "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta",
            "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha",
            "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada",
            "Uttara Bhadrapada", "Revati"
        ]
        
        # Major afflictions definitions
        self.AFFLICTIONS = {
            'sade_sathi': {
                'name': 'Sade Sathi',
                'description': 'Saturn transit through 12th, 1st, and 2nd houses from Moon sign',
                'duration_years': 7.5,
                'severity': 'High',
                'effects': 'Career challenges, health issues, relationship stress, financial constraints'
            },
            'ashtama_shani': {
                'name': 'Ashtama Shani',
                'description': 'Saturn transit through 8th house from Moon sign',
                'duration_years': 2.5,
                'severity': 'Very High',
                'effects': 'Major transformations, hidden enemies, accidents, chronic health issues'
            },
            'kuja_dosha': {
                'name': 'Kuja Dosha (Manglik)',
                'description': 'Mars in 1st, 2nd, 4th, 7th, 8th, or 12th house',
                'duration_years': 'Lifetime',
                'severity': 'Medium to High',
                'effects': 'Marital discord, delayed marriage, aggressive nature, accidents'
            },
            'kala_sarpa_dosha': {
                'name': 'Kala Sarpa Dosha',
                'description': 'All planets between Rahu and Ketu axis',
                'duration_years': 'Lifetime',
                'severity': 'High',
                'effects': 'Obstacles in life, delays in success, mental stress, spiritual growth'
            },
            'guru_chandal_yoga': {
                'name': 'Guru Chandal Yoga',
                'description': 'Jupiter conjunct with Rahu',
                'duration_years': 'Variable',
                'severity': 'Medium',
                'effects': 'Confusion in judgment, unconventional thinking, spiritual conflicts'
            },
            'rahu_mahadasha': {
                'name': 'Rahu Mahadasha',
                'description': 'Major period of Rahu (18 years)',
                'duration_years': 18,
                'severity': 'Medium to High',
                'effects': 'Illusions, foreign connections, material desires, unconventional path'
            },
            'ketu_mahadasha': {
                'name': 'Ketu Mahadasha',
                'description': 'Major period of Ketu (7 years)',
                'duration_years': 7,
                'severity': 'Medium',
                'effects': 'Detachment, spiritual growth, losses, isolation tendencies'
            }
        }

    def julian_day(self, date) -> float:
        """Convert datetime or date to Julian day"""
        # Handle both datetime.datetime and datetime.date objects
        if hasattr(date, 'hour'):
            # datetime object
            return swe.julday(date.year, date.month, date.day, 
                             date.hour + date.minute/60.0 + date.second/3600.0)
        else:
            # date object - use noon as default time
            return swe.julday(date.year, date.month, date.day, 12.0)

    def get_planet_position(self, planet: str, jd: float) -> Dict:
        """Get planet position for given Julian day"""
        try:
            if planet == 'ketu':
                # Ketu is 180° opposite to Rahu
                rahu_pos = swe.calc_ut(jd, self.PLANETS['rahu'])[0][0]
                longitude = (rahu_pos + 180) % 360
            else:
                result = swe.calc_ut(jd, self.PLANETS[planet])
                longitude = result[0][0]
            
            # Convert to sign and degree
            sign_num = int(longitude // 30)
            degree = longitude % 30
            
            return {
                'longitude': longitude,
                'sign': sign_num + 1,  # 1-12
                'degree': degree,
                'sign_name': self.get_sign_name(sign_num + 1)
            }
        except Exception as e:
            return None

    def get_sign_name(self, sign_num: int) -> str:
        """Get sign name from number"""
        signs = [
            "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
            "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
        ]
        return signs[sign_num - 1] if 1 <= sign_num <= 12 else "Unknown"

    def get_moon_sign(self, birth_date) -> Optional[int]:
        """Get Moon sign at birth"""
        jd = self.julian_day(birth_date)
        moon_pos = self.get_planet_position('moon', jd)
        return moon_pos['sign'] if moon_pos else None

    def calculate_sade_sathi_periods(self, birth_date) -> List[Dict]:
        """Calculate all Sade Sathi periods from birth to 100 years"""
        moon_sign = self.get_moon_sign(birth_date)
        if not moon_sign:
            return []
        
        sade_sathi_periods = []
        # Convert date to datetime for calculations
        if not hasattr(birth_date, 'hour'):
            from datetime import datetime
            current_date = datetime(birth_date.year, birth_date.month, birth_date.day)
            end_date = datetime(birth_date.year + 100, birth_date.month, birth_date.day)
        else:
            current_date = birth_date
            end_date = birth_date + timedelta(days=365 * 100)  # 100 years
        
        # Saturn takes about 29.5 years to complete one cycle
        # Sade Sathi occurs when Saturn transits 12th, 1st, and 2nd houses from Moon sign
        saturn_cycle_days = int(29.5 * 365.25)
        
        cycle_count = 0
        while current_date < end_date and cycle_count < 4:  # Max 4 cycles in 100 years
            # Calculate Saturn's position
            jd = self.julian_day(current_date)
            saturn_pos = self.get_planet_position('saturn', jd)
            
            if saturn_pos:
                saturn_sign = saturn_pos['sign']
                
                # Check if Saturn is in 12th, 1st, or 2nd house from Moon sign
                houses_from_moon = []
                for house in [12, 1, 2]:
                    target_sign = ((moon_sign + house - 2) % 12) + 1
                    houses_from_moon.append(target_sign)
                
                if saturn_sign in houses_from_moon:
                    # Find the start and end of this Sade Sathi period
                    sade_sathi_start = current_date
                    sade_sathi_end = current_date + timedelta(days=int(7.5 * 365.25))
                    
                    # Determine which phase (Rising, Peak, Setting)
                    if saturn_sign == houses_from_moon[0]:  # 12th house
                        phase = "Rising (Arohini)"
                        intensity = "Moderate"
                    elif saturn_sign == houses_from_moon[1]:  # 1st house
                        phase = "Peak (Madhya)"
                        intensity = "High"
                    else:  # 2nd house
                        phase = "Setting (Avarohi)"
                        intensity = "Moderate"
                    
                    sade_sathi_periods.append({
                        'name': 'Sade Sathi',
                        'phase': phase,
                        'intensity': intensity,
                        'start_date': sade_sathi_start,
                        'end_date': sade_sathi_end,
                        'start_age': self.calculate_age(birth_date, sade_sathi_start),
                        'end_age': self.calculate_age(birth_date, sade_sathi_end),
                        'duration_years': 7.5,
                        'moon_sign': self.get_sign_name(moon_sign),
                        'saturn_house': house,
                        'effects': self.get_sade_sathi_effects(phase),
                        'remedies': self.get_sade_sathi_remedies(phase)
                    })
                    
                    cycle_count += 1
            
            # Move to next Saturn cycle
            current_date += timedelta(days=saturn_cycle_days)
        
        return sade_sathi_periods

    def calculate_ashtama_shani_periods(self, birth_date) -> List[Dict]:
        """Calculate Ashtama Shani (8th house Saturn transit) periods"""
        moon_sign = self.get_moon_sign(birth_date)
        if not moon_sign:
            return []
        
        ashtama_periods = []
        # Convert date to datetime for calculations
        if not hasattr(birth_date, 'hour'):
            from datetime import datetime
            current_date = datetime(birth_date.year, birth_date.month, birth_date.day)
            end_date = datetime(birth_date.year + 100, birth_date.month, birth_date.day)
        else:
            current_date = birth_date
            end_date = birth_date + timedelta(days=365 * 100)
        
        # Saturn takes about 2.5 years to transit through each sign
        saturn_sign_transit_days = int(2.5 * 365.25)
        
        cycle_count = 0
        while current_date < end_date and cycle_count < 4:
            jd = self.julian_day(current_date)
            saturn_pos = self.get_planet_position('saturn', jd)
            
            if saturn_pos:
                saturn_sign = saturn_pos['sign']
                eighth_house_sign = ((moon_sign + 6) % 12) + 1  # 8th house from Moon
                
                if saturn_sign == eighth_house_sign:
                    ashtama_start = current_date
                    ashtama_end = current_date + timedelta(days=saturn_sign_transit_days)
                    
                    ashtama_periods.append({
                        'name': 'Ashtama Shani',
                        'start_date': ashtama_start,
                        'end_date': ashtama_end,
                        'start_age': self.calculate_age(birth_date, ashtama_start),
                        'end_age': self.calculate_age(birth_date, ashtama_end),
                        'duration_years': 2.5,
                        'intensity': 'Very High',
                        'moon_sign': self.get_sign_name(moon_sign),
                        'effects': 'Major life transformations, hidden challenges, health issues, accidents, inheritance matters',
                        'remedies': 'Hanuman Chalisa, Saturn mantras, donate black items on Saturdays, help elderly people'
                    })
                    
                    cycle_count += 1
            
            # Move to next cycle
            current_date += timedelta(days=int(29.5 * 365.25))
        
        return ashtama_periods

    def check_kuja_dosha(self, birth_date) -> Dict:
        """Check for Kuja Dosha (Manglik) in birth chart"""
        jd = self.julian_day(birth_date)
        mars_pos = self.get_planet_position('mars', jd)
        
        if not mars_pos:
            return None
        
        mars_sign = mars_pos['sign']
        
        # Get Ascendant (approximate - would need birth time for accuracy)
        # For simplicity, using Sun sign as reference
        sun_pos = self.get_planet_position('sun', jd)
        if not sun_pos:
            return None
        
        ascendant_sign = sun_pos['sign']  # Approximation
        
        # Calculate house position of Mars from Ascendant
        mars_house = ((mars_sign - ascendant_sign) % 12) + 1
        
        # Kuja Dosha houses: 1, 2, 4, 7, 8, 12
        kuja_dosha_houses = [1, 2, 4, 7, 8, 12]
        
        has_kuja_dosha = mars_house in kuja_dosha_houses
        
        if has_kuja_dosha:
            # Determine severity based on house
            if mars_house in [1, 8]:
                severity = "High"
                effects = "Strong aggressive tendencies, marital conflicts, accidents"
            elif mars_house in [2, 7, 12]:
                severity = "Medium"
                effects = "Moderate marital issues, family conflicts, financial disputes"
            else:  # house 4
                severity = "Low"
                effects = "Minor domestic issues, property disputes"
            
            return {
                'name': 'Kuja Dosha (Manglik)',
                'present': True,
                'mars_house': mars_house,
                'mars_sign': self.get_sign_name(mars_sign),
                'severity': severity,
                'effects': effects,
                'remedies': 'Hanuman worship, Tuesday fasting, Mars mantras, coral gemstone, marry another Manglik',
                'marriage_compatibility': 'Should marry another Manglik or perform specific remedies'
            }
        
        return {
            'name': 'Kuja Dosha (Manglik)',
            'present': False,
            'mars_house': mars_house,
            'mars_sign': self.get_sign_name(mars_sign),
            'effects': 'No Manglik dosha present',
            'marriage_compatibility': 'Normal marriage compatibility'
        }

    def check_kala_sarpa_dosha(self, birth_date) -> Dict:
        """Check for Kala Sarpa Dosha in birth chart"""
        jd = self.julian_day(birth_date)
        
        # Get all planet positions
        planets = ['sun', 'moon', 'mars', 'mercury', 'jupiter', 'venus', 'saturn']
        planet_positions = {}
        
        for planet in planets:
            pos = self.get_planet_position(planet, jd)
            if pos:
                planet_positions[planet] = pos['longitude']
        
        # Get Rahu position
        rahu_pos = self.get_planet_position('rahu', jd)
        ketu_pos = self.get_planet_position('ketu', jd)
        
        if not rahu_pos or not ketu_pos or len(planet_positions) < 7:
            return None
        
        rahu_long = rahu_pos['longitude']
        ketu_long = ketu_pos['longitude']
        
        # Check if all planets are between Rahu and Ketu
        planets_between_nodes = 0
        total_planets = len(planet_positions)
        
        for planet, longitude in planet_positions.items():
            # Check if planet is between Rahu and Ketu
            if rahu_long < ketu_long:
                if rahu_long <= longitude <= ketu_long:
                    planets_between_nodes += 1
            else:  # Rahu-Ketu axis crosses 0°
                if longitude >= rahu_long or longitude <= ketu_long:
                    planets_between_nodes += 1
        
        has_kala_sarpa = planets_between_nodes == total_planets
        
        if has_kala_sarpa:
            # Determine type based on which node is in which house
            return {
                'name': 'Kala Sarpa Dosha',
                'present': True,
                'intensity': 'High',
                'rahu_sign': rahu_pos['sign_name'],
                'ketu_sign': ketu_pos['sign_name'],
                'effects': 'Obstacles in life progress, delays in success, mental agitation, but also spiritual growth',
                'remedies': 'Rahu-Ketu mantras, visit Kalahasti temple, donate to serpent deities, perform Sarpa Dosha Nivarana',
                'positive_aspects': 'Strong intuition, spiritual inclinations, ability to overcome major obstacles'
            }
        
        return {
            'name': 'Kala Sarpa Dosha',
            'present': False,
            'effects': 'No Kala Sarpa Dosha present'
        }

    def calculate_age(self, birth_date, target_date) -> float:
        """Calculate age at target date"""
        # Handle both datetime and date objects
        if hasattr(birth_date, 'hour') and hasattr(target_date, 'hour'):
            delta = target_date - birth_date
        else:
            # Convert to date objects if needed
            birth_date_obj = birth_date.date() if hasattr(birth_date, 'date') else birth_date
            target_date_obj = target_date.date() if hasattr(target_date, 'date') else target_date
            delta = target_date_obj - birth_date_obj
        return round(delta.days / 365.25, 1)

    def get_sade_sathi_effects(self, phase: str) -> str:
        """Get effects based on Sade Sathi phase"""
        effects = {
            "Rising (Arohini)": "Initial challenges, career changes, new responsibilities, mild health issues",
            "Peak (Madhya)": "Maximum challenges, major life changes, health problems, relationship stress, financial constraints",
            "Setting (Avarohi)": "Gradual relief, lessons learned, rebuilding phase, improved wisdom"
        }
        return effects.get(phase, "General Sade Sathi effects")

    def get_sade_sathi_remedies(self, phase: str) -> str:
        """Get remedies based on Sade Sathi phase"""
        return "Saturday fasting, Hanuman Chalisa, Saturn mantras, donate black items, help elderly, wear blue sapphire (after consultation)"

    def get_complete_afflictions_timeline(self, birth_date) -> Dict:
        """Get complete afflictions timeline from birth to 100 years"""
        timeline = {
            'birth_date': birth_date,
            'sade_sathi_periods': self.calculate_sade_sathi_periods(birth_date),
            'ashtama_shani_periods': self.calculate_ashtama_shani_periods(birth_date),
            'kuja_dosha': self.check_kuja_dosha(birth_date),
            'kala_sarpa_dosha': self.check_kala_sarpa_dosha(birth_date),
            'summary': {}
        }
        
        # Add summary statistics
        total_sade_sathi_years = len(timeline['sade_sathi_periods']) * 7.5
        total_ashtama_years = len(timeline['ashtama_shani_periods']) * 2.5
        
        timeline['summary'] = {
            'total_sade_sathi_periods': len(timeline['sade_sathi_periods']),
            'total_sade_sathi_years': total_sade_sathi_years,
            'total_ashtama_periods': len(timeline['ashtama_shani_periods']),
            'total_ashtama_years': total_ashtama_years,
            'lifetime_kuja_dosha': timeline['kuja_dosha']['present'] if timeline['kuja_dosha'] else False,
            'lifetime_kala_sarpa': timeline['kala_sarpa_dosha']['present'] if timeline['kala_sarpa_dosha'] else False
        }
        
        return timeline

    def get_current_afflictions(self, birth_date) -> List[Dict]:
        """Get currently active afflictions"""
        current_date = datetime.now()
        current_afflictions = []
        
        # Check current Sade Sathi
        sade_sathi_periods = self.calculate_sade_sathi_periods(birth_date)
        for period in sade_sathi_periods:
            if period['start_date'] <= current_date <= period['end_date']:
                period['status'] = 'Active Now'
                period['remaining_days'] = (period['end_date'] - current_date).days
                current_afflictions.append(period)
        
        # Check current Ashtama Shani
        ashtama_periods = self.calculate_ashtama_shani_periods(birth_date)
        for period in ashtama_periods:
            if period['start_date'] <= current_date <= period['end_date']:
                period['status'] = 'Active Now'
                period['remaining_days'] = (period['end_date'] - current_date).days
                current_afflictions.append(period)
        
        return current_afflictions

    def get_upcoming_afflictions(self, birth_date, years_ahead: int = 5) -> List[Dict]:
        """Get upcoming afflictions in next few years"""
        current_date = datetime.now()
        future_date = current_date + timedelta(days=365 * years_ahead)
        upcoming_afflictions = []
        
        # Check upcoming Sade Sathi
        sade_sathi_periods = self.calculate_sade_sathi_periods(birth_date)
        for period in sade_sathi_periods:
            if current_date < period['start_date'] <= future_date:
                period['status'] = 'Upcoming'
                period['days_until_start'] = (period['start_date'] - current_date).days
                upcoming_afflictions.append(period)
        
        # Check upcoming Ashtama Shani
        ashtama_periods = self.calculate_ashtama_shani_periods(birth_date)
        for period in ashtama_periods:
            if current_date < period['start_date'] <= future_date:
                period['status'] = 'Upcoming'
                period['days_until_start'] = (period['start_date'] - current_date).days
                upcoming_afflictions.append(period)
        
        # Sort by start date
        upcoming_afflictions.sort(key=lambda x: x['start_date'])
        
        return upcoming_afflictions
