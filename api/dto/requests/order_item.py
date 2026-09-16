from pydantic import BaseModel, Field

class CreateOrderItem(BaseModel):
    order_id: int = Field()
    ticket_id: int = Field()
