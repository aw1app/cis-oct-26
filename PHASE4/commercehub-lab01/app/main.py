from typing import Annotated

from fastapi import Depends, FastAPI, status

from .models import OrderRequest, OrderResponse
from .repository import InMemoryOrderRepository
from .service import OrderService

app = FastAPI(redoc_url=None)
repository = InMemoryOrderRepository()


def get_order_service() -> OrderService:
    return OrderService(repository)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    order: OrderRequest,
    service: Annotated[OrderService, Depends(get_order_service)],
) -> OrderResponse:
    return service.create_order(order)


@app.get("/orders", response_model=list[OrderResponse])
def list_orders(
    service: Annotated[OrderService, Depends(get_order_service)],
) -> list[OrderResponse]:
    return service.list_orders()