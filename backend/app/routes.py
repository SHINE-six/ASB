from fastapi import APIRouter, HTTPException, Body
from app.crawler import LinkedInCrawler
from app.credentials import get_credentials
from app.utils import export_to_csv, validate_profiles
import os
from typing import List, Optional

router = APIRouter()

@router.post("/crawl")
def crawl_linkedin(profiles: list[str]):
    try:
        # Validate profiles
        if not validate_profiles(profiles):
            raise HTTPException(status_code=400, detail="Invalid LinkedIn profile URLs provided")
            
        # Get credentials and initialize crawler
        username, password = get_credentials()
        crawler = LinkedInCrawler(username, password)
        
        # Crawl profiles
        results = crawler.crawl_profiles(profiles)
        
        # Export to CSV
        csv_path = export_to_csv(results)
        csv_filename = os.path.basename(csv_path) if csv_path else None
        
        # Return results with CSV file information
        return {
            "profiles": results,
            "csv_export": {
                "success": csv_path is not None,
                "filename": csv_filename,
                "path": csv_path
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))