from api.rest.routers import user, venue, ticket, event, event_ticket, order, order_item
from core.sql_db import migrate
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def create_app() -> FastAPI:
    migrate()
    new_app = FastAPI()
    new_app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost",
            "http://localhost:8080",
            "http://localhost:5174",
            "http://127.0.0.1:5174",
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ],
        allow_methods=["*"],
        allow_headers=["*"]
    )
    new_app.include_router(user.router)
    new_app.include_router(venue.router)
    new_app.include_router(ticket.router)
    new_app.include_router(event.router)
    new_app.include_router(event_ticket.router)
    new_app.include_router(order.router)
    new_app.include_router(order_item.router)

    return new_app


app = create_app()