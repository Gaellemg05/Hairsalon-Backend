from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Availability, Appointment, Chat, Message
from .serializers import (
    AvailabilitySerializer, AppointmentSerializer,
    ChatSerializer, MessageSerializer
)

class AvailabilityViewSet(viewsets.ModelViewSet):
    queryset = Availability.objects.all()
    serializer_class = AvailabilitySerializer

    def get_queryset(self):
        hairdresser_id = self.request.query_params.get('hairdresser')
        if hairdresser_id:
            return self.queryset.filter(hairdresser_id=hairdresser_id)
        return self.queryset

    def perform_create(self, serializer):
        if 'hairdresser' in self.request.data and self.request.user.role in ['admin', 'hairdresser']:
            serializer.save()
        else:
            serializer.save(hairdresser=self.request.user)

class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return self.queryset
        elif user.role == 'hairdresser':
            return self.queryset.filter(hairdresser=user)
        else:
            return self.queryset.filter(client=user)

    def perform_create(self, serializer):
        if self.request.user.role == 'admin' and 'client' in self.request.data:
            serializer.save()
        else:
            serializer.save(client=self.request.user)

class ChatViewSet(viewsets.ModelViewSet):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return self.queryset
        elif user.role == 'hairdresser':
            return self.queryset.filter(hairdresser=user)
        else:
            return self.queryset.filter(client=user)

    def perform_create(self, serializer):
        user = self.request.user
        if user.role == 'hairdresser':
            serializer.save(hairdresser=user)
        else:
            serializer.save(client=user)

    @action(detail=False, methods=['post'])
    def find_or_create(self, request):
        client_id = request.data.get('client')
        hairdresser_id = request.data.get('hairdresser')
        salon_id = request.data.get('salon')
        if not all([client_id, hairdresser_id, salon_id]):
            return Response({'detail': 'client, hairdresser and salon are required.'}, status=status.HTTP_400_BAD_REQUEST)
        chat = Chat.objects.filter(
            client_id=client_id,
            hairdresser_id=hairdresser_id,
            salon_id=salon_id
        ).first()
        if chat:
            serializer = self.get_serializer(chat)
            return Response(serializer.data)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        chat = self.get_object()
        messages = chat.messages.all()
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        chat = self.get_object()
        content = request.data.get('content')
        if not content:
            return Response({'detail': 'Content is required.'}, status=status.HTTP_400_BAD_REQUEST)
        message = Message.objects.create(
            chat=chat,
            sender=request.user,
            content=content
        )
        serializer = MessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class MessageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .chatbot import get_response

@csrf_exempt
def chatbot_view(request):
    if request.method == 'POST':
        import json
        try:
            data = json.loads(request.body)
            message = data.get('message', '')
            response = get_response(message)
            return JsonResponse({'response': response})
        except (json.JSONDecodeError, KeyError):
            return JsonResponse({'response': 'Désolé, je n\'ai pas compris. Envoie un message texte.'}, status=400)
    return JsonResponse({'error': 'Method not allowed'}, status=405)
