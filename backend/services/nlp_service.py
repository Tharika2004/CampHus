import re
from difflib import SequenceMatcher
from geopy.geocoders import Nominatim

# Geopy Setup
geolocator = Nominatim(user_agent="tn_event_bot_2026_final")

def get_similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

def extract_line_by_keywords(ocr_results, keywords):
    for res in ocr_results:
        if any(k in res['text'].upper() for k in keywords):
            return res['text'].strip()
    return ""

def extract_event_name(ocr_results):
    if not ocr_results: return "Unknown Event"
    sorted_data = sorted(ocr_results, key=lambda x: x['height'], reverse=True)
    return sorted_data[0]['text'].strip()


def extract_date_and_time(ocr_results):
    """
    Scans word-by-word to find a Month and pairs it with 2026.
    Returns: "MONTH 2026", "10:00 AM"
    """
    m_map = {'JAN':'01','FEB':'02','MAR':'03','APR':'04','MAY':'05','JUN':'06',
             'JUL':'07','AUG':'08','SEP':'09','OCT':'10','NOV':'11','DEC':'12'}
    
    event_time = "10:00 AM" # Default Time
    found_month = None

    for res in ocr_results:
        # Full line-ai words-ah split pannuvom
        line_text = res['text'].upper()
        words = line_text.split() 

        for word in words:
            # Ovvoru word-um month name-la start aagudha-nu check pannuvom
            for m_key in m_map.keys():
                if word.startswith(m_key):
                    found_month = m_key
                    break 
            if found_month: break
        if found_month: break

    # Date format calculation
    if found_month:
        event_date = f"{found_month} 2026"
    else:
        # Month kidaikkalana ippo irukkara current month + 2026
        from datetime import datetime
        event_date = datetime.now().strftime("%b").upper() + " 2026"

    return event_date, event_time
def extract_metadata(ocr_results):
    # 1. Reference Lists (Keywords)
    tn_cities = [
        "CHENNAI", "COIMBATORE", "MADURAI", "TRICHY", "TIRUCHIRAPPALLI",
        "SALEM", "TIRUPPUR", "ERODE", "VELLORE", "THOOTHUKUDI",
        "TIRUNELVELI", "THANJAVUR", "DINDIGUL", "RANIPET", "SIVAKASI"
    ]
    venue_keywords = ["SEMINAR HALL", "AUDITORIUM", "BLOCK", "CAMPUS", "ARANGAM", "CONFERENCE HALL"]

    # --- 2. COLLEGE NAME: Fixed to remove Venue details from its line ---
    college_raw = extract_line_by_keywords(ocr_results, ["COLLEGE", "UNIVERSITY", "INSTITUTE", "ENGINEERING", "TECHNOLOGY", "CAMPUS"])
    college = "Unknown Institution"
    
    if college_raw:
        college = college_raw
        # Line kulla venue keyword edhavadhu irundha, adha cut panni college-ai clean pannuvom
        for v_key in venue_keywords:
            if v_key in college.upper():
                idx = college.upper().find(v_key)
                # Keyword-ku munnadi irukkara text-ai mattum college-ah eduppom
                college = college[:idx].strip().rstrip(',').rstrip(':')
                break
    
    if not college: college = "Unknown Institution"

    # --- 3. CITY SCANNER: Unchanged ---
    city_name = "Unknown City"
    for res in ocr_results:
        words = re.findall(r'[A-Z]+', res['text'].upper())
        for word in words:
            if len(word) < 4: continue
            if word in tn_cities:
                city_name = word
                break
            for ref in tn_cities:
                if get_similarity(word, ref) > 0.85:
                    city_name = ref
                    break
            if city_name != "Unknown City": break
        if city_name != "Unknown City": break

    # --- 4. EVENT TYPE: Unchanged (Keeping your previous cutting logic) ---
    event_keywords = ["SYMPOSIUM", "WORKSHOP", "CONFERENCE", "HACKATHON", "CULTURAL", "NATIONAL LEVEL", "EXPO", "MEET", "FEST"]
    e_type_raw = extract_line_by_keywords(ocr_results, event_keywords)
    e_type = "on poster"
    if e_type_raw:
        upper_e = e_type_raw.upper()
        cut_pos = -1
        for k in event_keywords:
            idx = upper_e.find(k)
            if idx != -1:
                end_idx = idx + len(k)
                if end_idx > cut_pos: cut_pos = end_idx
        e_type = e_type_raw[:cut_pos].strip() if cut_pos != -1 else e_type_raw

    # --- 5. VENUE: Fixed to store Full Detail (College + Venue) ---
    venue_detail = extract_line_by_keywords(ocr_results, venue_keywords)
    
    if venue_detail:
        # Check if the venue line already has the college name to avoid "Madha College, Madha College Auditorium"
        if college.upper() in venue_detail.upper():
            venue = venue_detail
        else:
            venue = f"{college}, {venue_detail}"
    else:
        venue = college
    
    # --- 6. GEOLOCATION (Priority Search) ---
    lat, lon = 0.0, 0.0
    
    # Priority List: 1. Full Info -> 2. College+City -> 3. Only College
    search_queries = []
    if college != "Unknown Institution" and city_name != "Unknown City":
        search_queries.append(f"{college}, {city_name}, Tamil Nadu")
        search_queries.append(f"{college}, {city_name}")
    
    if college != "Unknown Institution":
        search_queries.append(college)

    for query in search_queries:
        try:
            # timeout=10 kuduppom so search accurate-ah nadakkum
            location = geolocator.geocode(query, timeout=10)
            if location:
                lat, lon = location.latitude, location.longitude
                break # Accurate result kidaichidichu, so loop-ai stop pannidalaam
        except Exception as e:
            print(f"Geopy Error for {query}: {e}")
            continue

    # Oru vela mela irukka 3-um work aagallana mattum City level-ku pogum
    if lat == 0.0 and city_name != "Unknown City":
        try:
            loc_city = geolocator.geocode(f"{city_name}, Tamil Nadu", timeout=5)
            if loc_city:
                lat, lon = loc_city.latitude, loc_city.longitude
        except:
            pass
    description = extract_full_description(ocr_results)
    
    is_verified = 0

    return e_type, city_name, "Tamil Nadu", venue, lat, lon, college, description, is_verified


def extract_full_description(ocr_results):
    # OCR results-la irukkara ella line-aiyum oru list-ah eduthu, 
    # join panni oru single paragraph-ah mathuvom.
    full_text_list = [res['text'].strip() for res in ocr_results]
    
    # Lines-ai space vachu join pannuvom (Paragraph format)
    full_paragraph = " ".join(full_text_list)
    
    # Extra spaces clean panna logic
    full_paragraph = " ".join(full_paragraph.split())
    
    return full_paragraph if full_paragraph else "No text extracted from poster"