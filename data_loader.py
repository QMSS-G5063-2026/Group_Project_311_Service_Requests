import pandas as pd
import streamlit as st

@st.cache_data
def load_data():
    # Using the direct download link for large files
    # The 'id' comes from my shared link
    file_id = "1RmgSdmA2lt9XoBFVd-VDZU4gWTDdxK8I"
    url = f"https://drive.google.com/uc?export=download&id={file_id}&confirm=t"
    
    # Adding a status message so users know it's loading a large file
    try:
        df = pd.read_csv(url, low_memory=False)
    except Exception as e:
        st.error("Connection to Google Drive failed. Ensure the link is set to 'Anyone with the link can view'.")
        # Fallback to local file for terminal testing
        try:
            df = pd.read_csv("NYC_311_2025_Filtered.csv", low_memory=False)
        except:
            return pd.DataFrame()

    # Only keeping the columns we actually use.
    cols_to_keep = ['Borough', 'Neighborhood', 'Complaint', 'Latitude', 'Longitude', 'Incident Zip','Created Date']
    df = df[cols_to_keep].copy()
    
    # Limiting to Manhattan
    df = df[df['Borough'] == "MANHATTAN"].copy()
    
    # Numeric Coordinate Enforcement (Fixing blank maps)
    df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
    df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
    df = df.dropna(subset=["Latitude", "Longitude"])
    
    # Cleaning ZIP Codes (Strings without decimals)
    df['Incident Zip'] = df['Incident Zip'].fillna(0).astype(int).astype(str)
    
    # ─────────────────────────────────────────────
    # SAFE DATE PARSING (FIX FOR .dt ERROR) added for Over Time part
    # ─────────────────────────────────────────────
    df["Created Date"] = pd.to_datetime(df["Created Date"], errors="coerce")
    
    # DROP invalid dates BEFORE using .dt
    df = df.dropna(subset=["Created Date"])
    
    # NOW safe to use .dt
    df["Month"] = df["Created Date"].dt.to_period("M")
    
    
    # Cleaning Neighborhoods (Ensures the drop-down is clean)
    df = df.dropna(subset=["Neighborhood"])

    # The new mapping Logic
    category_map = {
        # Noise Issues
        "Noise - Residential": "Noise Issues",
        "Noise - Street/Sidewalk": "Noise Issues",
        "Noise - Commercial": "Noise Issues",
        "Noise - Vehicle": "Noise Issues",
        "Noise - Helicopter": "Noise Issues",
        "Noise - Park": "Noise Issues",
        "Noise - House of Worship": "Noise Issues",
        "Noise": "Noise Issues",

        # Sanitation & Waste
        "Dirty Condition": "Sanitation & Waste",
        "Illegal Dumping": "Sanitation & Waste",
        "Litter Basket Complaint": "Sanitation & Waste",
        "Litter Basket Request": "Sanitation & Waste",
        "Missed Collection": "Sanitation & Waste",
        "Recycling Basket Complaint": "Sanitation & Waste",
        "Residential Disposal Complaint": "Sanitation & Waste",
        "Commercial Disposal Complaint": "Sanitation & Waste",
        "Institution Disposal Complaint": "Sanitation & Waste",
        "Street Sweeping Complaint": "Sanitation & Waste",
        "Dumpster Complaint": "Sanitation & Waste",
        "Adopt-A-Basket": "Sanitation & Waste",

        # Street & Infrastructure
        "Street Condition": "Street & Infrastructure",
        "Sidewalk Condition": "Street & Infrastructure",
        "Curb Condition": "Street & Infrastructure",
        "Highway Condition": "Street & Infrastructure",
        "DEP Highway Condition": "Street & Infrastructure",
        "Bridge Condition": "Street & Infrastructure",
        "Tunnel Condition": "Street & Infrastructure",
        "Street Light Condition": "Street & Infrastructure",
        "Traffic Signal Condition": "Street & Infrastructure",
        "Broken Parking Meter": "Street & Infrastructure",
        "Street Sign - Damaged": "Street & Infrastructure",
        "Street Sign - Missing": "Street & Infrastructure",
        "Street Sign - Dangling": "Street & Infrastructure",
        "Highway Sign - Damaged": "Street & Infrastructure",
        "Highway Sign - Missing": "Street & Infrastructure",
        "Highway Sign - Dangling": "Street & Infrastructure",
        "Obstruction": "Street & Infrastructure",

        # Parking & Vehicles
        "Illegal Parking": "Parking & Vehicles",
        "Blocked Driveway": "Parking & Vehicles",
        "Abandoned Vehicle": "Parking & Vehicles",
        "Derelict Vehicles": "Parking & Vehicles",
        "E-Scooter": "Parking & Vehicles",
        "Bike Rack": "Parking & Vehicles",
        "Bike Rack Condition": "Parking & Vehicles",
        "Abandoned Bike": "Parking & Vehicles",
        "Municipal Parking Facility": "Parking & Vehicles",

        # Public Safety & Illegal Activity
        "Drug Activity": "Public Safety & Illegal Activity",
        "Illegal Posting": "Public Safety & Illegal Activity",
        "Graffiti": "Public Safety & Illegal Activity",
        "Drinking": "Public Safety & Illegal Activity",
        "Disorderly Youth": "Public Safety & Illegal Activity",
        "Non-Emergency Police Matter": "Public Safety & Illegal Activity",
        "Investigations and Discipline (IAD)": "Public Safety & Illegal Activity",
        "Illegal Fireworks": "Public Safety & Illegal Activity",
        "Posting Advertisement": "Public Safety & Illegal Activity",

        # Buildings & Property
        "Building/Use": "Buildings & Property",
        "Building Condition": "Buildings & Property",
        "General Construction/Plumbing": "Buildings & Property",
        "Construction Safety Enforcement": "Buildings & Property",
        "Boilers": "Buildings & Property",
        "Plumbing": "Buildings & Property",
        "Electrical": "Buildings & Property",
        "Elevator": "Buildings & Property",
        "Facade Insp Safety Pgm": "Buildings & Property",
        "Stalled Sites": "Buildings & Property",
        "Window Guard": "Buildings & Property",
        "Building Drinking Water Tank": "Buildings & Property",
        "Construction Lead Dust": "Buildings & Property",
        "BEST/Site Safety": "Buildings & Property",
        "Scaffold Safety": "Buildings & Property",
        "Cranes and Derricks": "Buildings & Property",
        "Building Marshal's Office": "Buildings & Property",

        # Health & Environmental
        "Air Quality": "Health & Environmental",
        "Indoor Air Quality": "Health & Environmental",
        "Water Quality": "Health & Environmental",
        "Drinking Water": "Health & Environmental",
        "Lead": "Health & Environmental",
        "Asbestos": "Health & Environmental",
        "Mold": "Health & Environmental",
        "Hazardous Materials": "Health & Environmental",
        "Food Poisoning": "Health & Environmental",
        "Cooling Tower": "Health & Environmental",
        "Radioactive Material": "Health & Environmental",
        "Water Conservation": "Health & Environmental",
        "Standing Water": "Health & Environmental",
        "Industrial Waste": "Health & Environmental",
        "Sustainability Enforcement": "Health & Environmental",

        # Animals & Pests
        "Rodent": "Animals & Pests",
        "Dead Animal": "Animals & Pests",
        "Unleashed Dog": "Animals & Pests",
        "Animal-Abuse": "Animals & Pests",
        "Animal in a Park": "Animals & Pests",
        "Illegal Animal Kept as Pet": "Animals & Pests",
        "Mosquitoes": "Animals & Pests",
        "Unsanitary Animal Pvt Property": "Animals & Pests",
        "Unsanitary Animal Facility": "Animals & Pests",
        "Harboring Bees/Wasps": "Animals & Pests",

        # Trees, Parks & Nature
        "Damaged Tree": "Trees, Parks & Nature",
        "Dead/Dying Tree": "Trees, Parks & Nature",
        "Overgrown Tree/Branches": "Trees, Parks & Nature",
        "Root/Sewer/Sidewalk Condition": "Trees, Parks & Nature",
        "New Tree Request": "Trees, Parks & Nature",
        "Uprooted Stump": "Trees, Parks & Nature",
        "Plant": "Trees, Parks & Nature",
        "Special Natural Area District (SNAD)": "Trees, Parks & Nature",
        "Beach/Pool/Sauna Complaint": "Trees, Parks & Nature",
        "Lifeguard": "Trees, Parks & Nature",

        # Transportation & Commercial Services
        "Taxi Complaint": "Transportation & Commercial Services",
        "Taxi Report": "Transportation & Commercial Services",
        "Taxi Compliment": "Transportation & Commercial Services",
        "For Hire Vehicle Complaint": "Transportation & Commercial Services",
        "For Hire Vehicle Report": "Transportation & Commercial Services",
        "FHV Licensee Complaint": "Transportation & Commercial Services",
        "Green Taxi Complaint": "Transportation & Commercial Services",
        "Green Taxi Report": "Transportation & Commercial Services",
        "Vendor Enforcement": "Transportation & Commercial Services",
        "Mobile Food Vendor": "Transportation & Commercial Services",
        "Outdoor Dining": "Transportation & Commercial Services",
        "Bus Stop Shelter Complaint": "Transportation & Commercial Services",
        "Bus Stop Shelter Placement": "Transportation & Commercial Services",
        "Ferry Inquiry": "Transportation & Commercial Services",
        "Ferry Complaint": "Transportation & Commercial Services",

        # Social Services & Other
        "Homeless Person Assistance": "Other",
        "Lost Property": "Other",
        "Found Property": "Other",
        "Consumer Complaint": "Other",
        "Day Care": "Other",
        "School Maintenance": "Other",
        "Public Toilet": "Other",
        "Borough Office": "Other",
        "Dept of Investigations": "Other",
        "Special Projects Inspection Team (SPIT)": "Other",
        "Special Operations": "Other",
        "LinkNYC": "Other",
        "Wayfinding": "Other",
        "Unspecified": "Other",
        "Incorrect Data": "Other",
    }

    # Creating the New Category Column
    df['Complaint_Group'] = df['Complaint'].map(category_map).fillna('Other')

    # Memory Optimization
    # Trying to keep the browser from crashing when loading citywide data
    df['Complaint_Group'] = df['Complaint_Group'].astype('category')
    df['Complaint'] = df['Complaint'].astype('category')
    df['Neighborhood'] = df['Neighborhood'].astype('category')
    
    # Coordinates must be floats for the map to work
    df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
    df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
    df = df.dropna(subset=['Latitude', 'Longitude'])

    return df