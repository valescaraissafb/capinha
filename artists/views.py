from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .models import Artista
from .serializers import ArtistaSerializer

class ArtistaViewSet(ModelViewSet):
    queryset = Artista.objects.filter(ativo=True)
    serializer_class = ArtistaSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

# Adicione uma view baseada em função para renderizar o template
def artista_list(request):
    artistas = Artista.objects.filter(ativo=True)
    return render(request, 'artists/artista_list.html', {'artistas': artistas})
