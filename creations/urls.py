from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ColecaoViewSet, ArteViewSet, PersonalizacaoViewSet

router = DefaultRouter()
router.register(r'colecoes', ColecaoViewSet, basename='colecao')
router.register(r'artes', ArteViewSet, basename='arte')
router.register(r'personalizacoes', PersonalizacaoViewSet, basename='personalizacao')

urlpatterns = [
    path('', include(router.urls)),
]