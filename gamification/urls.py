from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RecompensaViewSet, UsuarioRecompensaViewSet

router = DefaultRouter()
router.register(r'recompensas', RecompensaViewSet, basename='recompensa')
router.register(r'usuario-recompensas', UsuarioRecompensaViewSet, basename='usuario-recompensa')

urlpatterns = [
    path('', include(router.urls)),
]