from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from main import days_ago, run_scraper
from database import show_businesses, update_businesses_status, get_business_count, get_dashboard_stats

import database

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
templates.env.filters["days_ago"] = days_ago


@app.get("/leads")
def leads_page(request: Request, status: str = "all", page: int = 1, search: str = ""):
    per_page = 10
    offset = (page-1) * per_page

    total_count = get_business_count("all")
    not_done_count = get_business_count("not_done")
    emailed_count = get_business_count("emailed")
    no_good_count = get_business_count("no_good")

    stats = get_dashboard_stats()

    businesses = show_businesses(status, search, per_page, offset)

    return templates.TemplateResponse(
        "leads.html",
        {
         "request": request, 
         "businesses": businesses,
         "current_status": status,
         "page": page,
         "search": search,

         "total_count": total_count,
         "not_done_count": not_done_count,
         "emailed_count": emailed_count,
         "no_good_count": no_good_count,
         "stats": stats,
        }
    )


@app.post("/leads/{business_id}/status")
def change_status(business_id: int, status: str = Form(...)):
    update_businesses_status(business_id, status)
    return RedirectResponse(url="/leads", status_code=303)


@app.post("/run-scraper")
def run_scraper_route():

    run_scraper()   

    return RedirectResponse("/leads", status_code=303)