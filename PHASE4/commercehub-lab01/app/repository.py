from threading import Lock
from typing import TypedDict

from .models import OrderItem, OrderResponse


class OrderData(TypedDict):
    customer_name: str
    items: list[OrderItem]
    total: float


class OrderRepository:
    def __init__(self) -> None:
        self._orders: list[OrderResponse] = []
        self._lock = Lock()

    def save(self, order: OrderData) -> OrderResponse:
        with self._lock:
            saved_order = OrderResponse(order_id=len(self._orders) + 1, **order)
            self._orders.append(saved_order.model_copy(deep=True))
            return saved_order

    def list_all(self) -> list[OrderResponse]:
        with self._lock:
            return [order.model_copy(deep=True) for order in self._orders]