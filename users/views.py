from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate
from .models import user
from .serializers import UserListSerializer, UserDetailSerializer, UserCreateSerializer

# Create your views here.

class UserViewSet(viewsets.ModelViewSet):
    queryset = user.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action == 'retrieve':
            return UserDetailSerializer
        return UserListSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return super().get_permissions()
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def perfil(self, request):
        """Retorna dados do usuário autenticado"""
        serializer = UserDetailSerializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def alterar_senha(self, request):
        """Altera a senha do usuário autenticado"""
        user = request.user
        senha_atual = request.data.get('senha_atual')
        senha_nova = request.data.get('senha_nova')
        
        if not authenticate(username=user.username, password=senha_atual):
            return Response(
                {'erro': 'Senha atual incorreta'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(senha_nova)
        user.save()
        return Response({'mensagem': 'Senha alterada com sucesso'})
