from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from .models import Recompensa, UsuarioRecompensa
from .serializers import RecompensaSerializer, UsuarioRecompensaSerializer


class RecompensaViewSet(viewsets.ModelViewSet):
    queryset = Recompensa.objects.all()
    serializer_class = RecompensaSerializer


class UsuarioRecompensaViewSet(viewsets.ModelViewSet):
    queryset = UsuarioRecompensa.objects.all()
    serializer_class = UsuarioRecompensaSerializer
    
    @action(detail=False, methods=['get'])
    def por_usuario(self, request):
        usuario_id = request.query_params.get('usuario_id')
        if not usuario_id:
            return Response({'erro': 'usuario_id é obrigatório'}, status=status.HTTP_400_BAD_REQUEST)
        
        recompensas = UsuarioRecompensa.objects.filter(usuario_id=usuario_id)
        serializer = self.get_serializer(recompensas, many=True)
        return Response(serializer.data)