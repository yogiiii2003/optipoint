from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from app.config import settings
from app.routers import amenities, apartments, optimality

limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])

app = FastAPI(
    title="Optipoint API",
    description="Location intelligence: NLP + geospatial + ML.",
    version="0.2.0",
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(apartments.router, prefix="/api/apartments", tags=["apartments"])
app.include_router(amenities.router, prefix="/api/amenities", tags=["amenities"])
app.include_router(optimality.router, prefix="/api/optimality", tags=["optimality"])


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
