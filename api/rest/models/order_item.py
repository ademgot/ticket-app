from pydantic import BaseModel, Field

class OrderItem(BaseModel):
    order_id: int = Field()
    ticket_id: int = Field()
    created_at: int = Field()
    updated_at: int = Field()
