from api.rest.routers import (
    event,
    order,
    order_item,
    seat,
    tax_rate,
    ticket,
    ticket_type,
    user,
    venue,
)
from api.core.utils.common import handle_integrity_error
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlite3 import IntegrityError


def create_app() -> FastAPI:
    new_app = FastAPI()
    new_app.add_exception_handler(IntegrityError, handle_integrity_error)
    new_app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"]
    )
    new_app.include_router(user.router)
    new_app.include_router(venue.router)
    new_app.include_router(ticket.router)
    new_app.include_router(event.router)
    new_app.include_router(ticket_type.router)
    new_app.include_router(order.router)
    new_app.include_router(order_item.router)
    new_app.include_router(seat.router)
    new_app.include_router(tax_rate.router)

    return new_app


app = create_app()