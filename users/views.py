from rest_framework import viewsets, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, get_user_model
from .serializers import UserSerializer, RegisterSerializer
from salons.models import Salon

User = get_user_model()

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            affiliated_salon_id = request.data.get('affiliated_salon_id')
            if affiliated_salon_id and user.role == 'hairdresser':
                try:
                    salon = Salon.objects.get(id=affiliated_salon_id)
                    salon.hairdressers.add(user)
                except Salon.DoesNotExist:
                    pass
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user': UserSerializer(user).data
            })
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve'] and self.request.user.is_authenticated:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        role_filter = self.request.query_params.get('role')
        if role_filter:
            return self.queryset.filter(role=role_filter)
        if self.request.user.role == 'admin':
            return self.queryset
        # Otherwise, limit to themselves or active hairdressers
        return self.queryset.filter(id=self.request.user.id) | self.queryset.filter(role='hairdresser')
