from .models import OrderRequest, OrderResponse
from .repository import OrderRepository


class OrderService:
    def __init__(self, repository: OrderRepository) -> None:
        self._repository = repository

    def calculate_total(self, order: OrderRequest) -> float:
        return round(
            sum(item.quantity * item.unit_price for item in order.items), 2
        )

    def create_order(self, order: OrderRequest) -> OrderResponse:
        total = self.calculate_total(order)
        return self._repository.save(
            {
                "customer_name": order.customer_name,
                "items": order.items,
                "total": total,
            }
        )

    def list_orders(self) -> list[OrderResponse]:
        return self._repository.list_all()