from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

from lifes_setup import lifespan
from routers.router_report_by_country import router_report_by_country
from routers.routers_report import router_report
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AbelHost Analyze API",
    lifespan=lifespan
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "127.0.0.1:8000",],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type","Set-Cookie", "Authorization", "Access-Control-Allow-Origin"]
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global error caught: {exc}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "message": "Internal Server Error",
            "detail": str(exc) #debug
        }
    )


app.include_router(router_report)
app.include_router(router_report_by_country)