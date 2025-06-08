# ASB Alumni LinkedIn Crawler

## Team name - The ASB alumni + 2 others

## Project Overview

The **ASB Alumni LinkedIn Crawler** is a one of two part solution designed to crawl and extract data from ASB alumni LinkedIn public profiles. This repository contains the backend code for the crawler, which is responsible for scraping LinkedIn profiles and company pages to gather relevant information about ASB alumni and their professional backgrounds.

This repository consist of only the backend component:
1. **Backend**: Built using Python to perform the actual web crawling, data extraction, and output generation.

### Features:
- Crawl LinkedIn public profiles (e.g., individuals' profiles, company pages)
- Extract detailed profile information:
  - **Personal Details**: Full Name, Gender, Profile Image, Location, Birthday
  - **Professional Info**: Current Position, Company, Duration, Position Level
  - **Background**: About Section, Skills, Languages, Education History
  - **Contact**: Email, Phone, Social Media, Websites
  - **Network**: Connection Count
  - **Company Data**: Company Name, Industry, Location, Overview
- Anti-bot mechanisms (headers, proxies, rate-limiting)
- Structured output in JSON format

## Requirements

### Backend:
The backend is built using **Python**. Below are the required dependencies:

**For Python:**
```bash
cd backend && uv sync
```

## Getting Started

To run this project, you need to set up the backend.

### Step 1: Set up the Backend

1. **Python Setup** (if using Python):
    - Install dependencies:
      ```bash
      cd backend
      uv sync or uv pip install -r backend/requirements.txt
      ```

    - Set up credentials:
      - Copy the `.env.example` file to `.env`:
        ```bash
        cp backend/.env.example backend/.env
        ```
      - Open the `.env` file and fill in the required fields:
      - Add your LinkedIn credentials to the `.env` file:
      - Add your api keys to the `.env` file:
      
    - Navigate to the `backend/` folder and run the backend server:
      ```bash
      python backend/main.py or uv run backend/main.py
      ```

## Usage example

```bash
curl -X 'POST' \
  'http://0.0.0.0:8000/crawl' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '[
  "https://www.linkedin.com/in/addis-olujohungbe/",
  "https://www.linkedin.com/in/sharanjm",
  "https://www.linkedin.com/in/poncesamaniego/",
  "https://www.linkedin.com/in/samuel-ler/",
  "https://www.linkedin.com/in/andrew-foley-6ba07779/",
  "https://www.linkedin.com/in/christophergbenavides/",
  "https://www.linkedin.com/in/mike-titzer-834a0535/",
  "https://www.linkedin.com/in/ktrobinson7/",
  "https://www.linkedin.com/in/natalie-ho-mba2018/",
  "https://www.linkedin.com/in/alexsnedeker/",
  "https://www.linkedin.com/in/sidgondode/",
  "https://www.linkedin.com/in/keitumetse-molamu/",
  "https://www.linkedin.com/in/jsehgal/",
  "https://www.linkedin.com/in/esther-siah-86a9a278/",
  "https://www.linkedin.com/in/dmitryvedenyapin/"
]'
```

