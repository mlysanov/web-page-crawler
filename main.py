from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi import FastAPI, Request
from crawler import WebCrawler

app = FastAPI()

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/crawl")
def crawl(query: str, depth: int = 2):
    if not query.startswith("http://") and not query.startswith("https://"):
        query = "http://" + query

    crawler = WebCrawler(start_url=query, max_depth=depth)
    return StreamingResponse(
        crawler.crawl_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"}
    )
