import os
import csv
from datetime import datetime
from typing import List, Dict, Any

def validate_profiles(profiles):
    return all(profile.startswith("https://www.linkedin.com/") for profile in profiles)

def export_to_csv(data: List[Dict[str, Any]], filename: str = None) -> str:
    """
    Export profile data to CSV file
    
    Args:
        data: List of profile dictionaries
        filename: Optional filename for the CSV file
    
    Returns:
        Path to the created CSV file
    """
    if not data:
        return None
        
    # Define column headers based on the expected profile structure
    fieldnames = [
      "Name",
      "Gender",
      "Profile Image",
      "LinkedIn URL",
      "Location",
      "Headline",
      "About",
      "Activity Posts",
      "Current Position",
      "Current Company",
      "Current Company Duration",
      "Education",
      "Education URLs",  
      "Degrees",
      "Connection Count",
      "Languages",
      "Skills",
      "Websites",
      "Contact Phone",
      "Contact Email",
      "Contact Twitter",
      "Birthday",
      "Position Level",
      "Updated Timestamp"
    ]
    
    # Create directory for CSV files if it doesn't exist
    csv_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "exports")
    os.makedirs(csv_dir, exist_ok=True)
    
    # Create filename with timestamp if not provided
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"linkedin_profiles_{timestamp}.csv"
    
    # Full path to the CSV file
    filepath = os.path.join(csv_dir, filename)
    
    # Write data to CSV
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        
        for profile in data:
            # Clean any None values to empty strings for CSV compatibility
            cleaned_profile = {k: (v if v is not None else '') for k, v in profile.items()}
            writer.writerow(cleaned_profile)
            
    return filepath
