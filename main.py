from database import setup_database, save_activity, show_businesses, update_businesses, searches_already_done, save_search
from datetime import date
import os
import requests


terms = ["landscaping", "junk removal", "roofing", "plumbing"]
cities = ["Modesto, CA", "Turlock, CA", "Manteca, CA", "Stockton, CA"]\

def fake_yelp_search(term, city):
    return [
        {
            "id": "fake_001",
            "name": "Test Landscaping Co",
            "display_phone": "(209) 555-1234",
            "url": "https://www.yelp.com/biz/test-landscaping"
        },
        {
            "id": "fake_002",
            "name": "Modesto Lawn Pros",
            "display_phone": "(209) 555-5678",
            "url": "https://www.yelp.com/biz/modesto-lawn-pros"
        },
        {
            "id": "fake_005",
            "name": "Test Landscaping Co",
            "display_phone": "(209) 555-1234",
            "url": "https://www.yelp.com/biz/test-landscaping"
        },
        {
            "id": "fake_003",
            "name": "Modesto Lawn Pros",
            "display_phone": "(209) 555-5678",
            "url": "https://www.yelp.com/biz/modesto-lawn-pros"
        },
        {
            "id": "fake_004",
            "name": "Test Landscaping Co",
            "display_phone": "(209) 555-1234",
            "url": "https://www.yelp.com/biz/test-landscaping"
        },
        {
            "id": "fake_006",
            "name": "Modesto Lawn Pros",
            "display_phone": "(209) 555-5678",
            "url": "https://www.yelp.com/biz/modesto-lawn-pros"
        },
        {
            "id": "fake_007",
            "name": "Test Landscaping Co",
            "display_phone": "(209) 555-1234",
            "url": "https://www.yelp.com/biz/test-landscaping"
        },
        {
            "id": "fake_008",
            "name": "Modesto Lawn Pros",
            "display_phone": "(209) 555-5678",
            "url": "https://www.yelp.com/biz/modesto-lawn-pros"
        },
        {
            "id": "fake_009",
            "name": "Test Landscaping Co",
            "display_phone": "(209) 555-1234",
            "url": "https://www.yelp.com/biz/test-landscaping"
        },
        {
            "id": "fake_010",
            "name": "Test Landscaping Co",
            "display_phone": "(209) 555-1234",
            "url": "https://www.yelp.com/biz/test-landscaping"
        },
        {
            "id": "fake_011",
            "name": "Test Landscaping Co",
            "display_phone": "(209) 555-1234",
            "url": "https://www.yelp.com/biz/test-landscaping"
        },
        {
            "id": "fake_012",
            "name": "Test Landscaping Co",
            "display_phone": "(209) 555-1234",
            "url": "https://www.yelp.com/biz/test-landscaping"
        },
        {
            "id": "fake_013",
            "name": "Test Landscaping Co",
            "display_phone": "(209) 555-1234",
            "url": "https://www.yelp.com/biz/test-landscaping"
        },
        {
            "id": "fake_015",
            "name": "Test Landscaping Co",
            "display_phone": "(209) 555-1234",
            "url": "https://www.yelp.com/biz/test-landscaping"
        },
        {
            "id": "fake_014",
            "name": "Test Landscaping Co",
            "display_phone": "(209) 555-1234",
            "url": "https://www.yelp.com/biz/test-landscaping"
        }
    ]


YELP_API_KEY = os.getenv("YELP_API_KEY")

def fetch_yelp_businesses(term, city, limit=20):
    url = "https://api.yelp.com/v3/businesses/search"

    headers = {
        "Authorization": f"Bearer {YELP_API_KEY}"
    }

    params = {
        "term": term,
        "location": city,
        "limit": limit
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    data = response.json()

    businesses = []

    for item in data.get("businesses", []):
        business = {
            "yelp_id": item.get("id"),
            "name": item.get("name"),
            "phone": item.get("display_phone"),
            "yelp_url": item.get("url"),
            "website": None,
            "email": None,
            "category": term,
            "city": city,
        }

        businesses.append(business)

    return businesses


def run_auto_search():
    #searching by city and term instead of input
    for city in cities:
        for term in terms:
            run_search(term, city)


def run_search(term, city):
    businesses = fake_yelp_search(term, city)

    total_added = 0

    for business in businesses: 
        added = save_activity(business, term, city)
        total_added += added

    print(f"Search complete.")
    print(f"Found: {len(businesses)}")
    print(f"New businesses added: {total_added}")    


def days_ago(created_at):
    if not created_at:
        return "Found recently"
    
    created = date.fromisoformat(created_at)
    today = date.today()

    days = (today - created).days

    if days == 0:
        return "Found today"
    elif days == 1:
        return "Found yesterday"
    elif days < 7:
        return f"Found {days} days ago"
    elif days < 14:
        return "Found 1 week ago"
    else:
        return f"Found {days // 7} weeks ago"


def run_scraper():
    setup_database()

    for category in terms:
        for city in cities:
            if searches_already_done(category, city):
                continue
            else:
                run_search(category, city)
                save_search(category, city)
    print("ran")


if __name__ == "__main__":
    run_scraper()