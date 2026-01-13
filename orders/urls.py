from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import PedidoViewSet, ItemPedidoViewSet

router = DefaultRouter()
router.register(r"orders", PedidoViewSet, basename="orders")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "orders/items/<int:pk>/",
        ItemPedidoViewSet.as_view({"put": "update", "delete": "destroy"}),
        name="order-item-detail",
    ),
]