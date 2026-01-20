from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ArtistaViewSet, artista_list

router = DefaultRouter()
router.register(r'artistas', ArtistaViewSet)

urlpatterns = [
    path('', artista_list, name='artista-list'),
    path('api/', include(router.urls)),
]
