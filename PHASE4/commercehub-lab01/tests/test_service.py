from app.models import OrderRequest
from app.repository import InMemoryOrderRepository
from app.service import OrderService


def build_order() -> OrderRequest:
    return OrderRequest(
        customer_name="Test Customer",
        items=[
            {"name": "Notebook", "quantity": 2, "unit_price": 50},
            {"name": "Pen", "quantity": 1, "unit_price": 20},
        ],
    )


def test_calculate_total_for_multiple_items() -> None:
    service = OrderService(InMemoryOrderRepository())

    assert service.calculate_total(build_order()) == 120.0


def test_created_order_can_be_listed() -> None:
    service = OrderService(InMemoryOrderRepository())
    created_order = service.create_order(build_order())

    assert service.list_orders() == [created_order]