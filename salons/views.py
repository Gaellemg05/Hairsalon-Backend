from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from datetime import timedelta
from .models import Salon, Service, SalonPublication, HairstylePublication, Review, SubscriptionTransaction
from .serializers import (
    SalonSerializer, ServiceSerializer, SalonPublicationSerializer,
    HairstylePublicationSerializer, ReviewSerializer,
    SubscriptionTransactionSerializer
)

class SalonViewSet(viewsets.ModelViewSet):
    queryset = Salon.objects.all()
    serializer_class = SalonSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        manager_id = self.request.query_params.get('manager')
        if manager_id:
            return self.queryset.filter(manager_id=manager_id)
        hairdresser_id = self.request.query_params.get('hairdresser')
        if hairdresser_id:
            return self.queryset.filter(hairdressers__id=hairdresser_id)
        return self.queryset

    def perform_create(self, serializer):
        now = timezone.now()
        trial_until = now + timedelta(days=7)
        salon = serializer.save(manager=self.request.user, subscription_active_until=trial_until)
        # Automatically add the manager as the first stylist if they are a hairdresser
        if self.request.user.role == 'hairdresser':
            salon.hairdressers.add(self.request.user)
        SubscriptionTransaction.objects.create(
            salon=salon,
            amount=0,
            operator='system',
            phone_number='',
            transaction_type='trial'
        )

    @action(detail=True, methods=['post'])
    def add_hairdresser(self, request, pk=None):
        salon = self.get_object()
        hairdresser_id = request.data.get('hairdresser_id')
        if not hairdresser_id:
            return Response({'error': 'hairdresser_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            hairdresser = User.objects.get(id=hairdresser_id, role='hairdresser')
            salon.hairdressers.add(hairdresser)
            return Response({'status': 'added'})
        except User.DoesNotExist:
            return Response({'error': 'Hairdresser not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def remove_hairdresser(self, request, pk=None):
        salon = self.get_object()
        hairdresser_id = request.data.get('hairdresser_id')
        if not hairdresser_id:
            return Response({'error': 'hairdresser_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        salon.hairdressers.remove(hairdresser_id)
        return Response({'status': 'removed'})

    @action(detail=True, methods=['post'])
    def subscribe(self, request, pk=None):
        salon = self.get_object()
        if salon.manager != request.user:
            return Response({'error': 'Only the manager can subscribe'}, status=status.HTTP_403_FORBIDDEN)
        phone = request.data.get('phone_number')
        operator = request.data.get('operator')
        if not phone or not operator:
            return Response({'error': 'phone_number and operator are required'}, status=status.HTTP_400_BAD_REQUEST)
        now = timezone.now()
        if salon.subscription_active_until and salon.subscription_active_until > now:
            salon.subscription_active_until += timedelta(days=30)
        else:
            salon.subscription_active_until = now + timedelta(days=30)
        salon.save()
        SubscriptionTransaction.objects.create(
            salon=salon,
            amount=10000,
            operator=operator,
            phone_number=phone,
            transaction_type='subscription'
        )
        return Response({
            'status': 'active',
            'subscription_active_until': salon.subscription_active_until,
            'message': f'Subscription activated via {operator} ({phone}). Valid until {salon.subscription_active_until.strftime("%Y-%m-%d")}.'
        })

    @action(detail=True, methods=['get'])
    def transactions(self, request, pk=None):
        salon = self.get_object()
        qs = salon.subscription_transactions.all().order_by('-created_at')
        serializer = SubscriptionTransactionSerializer(qs, many=True)
        return Response(serializer.data)

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        salon_id = self.request.query_params.get('salon')
        if salon_id:
            return self.queryset.filter(salon_id=salon_id)
        return self.queryset

class SalonPublicationViewSet(viewsets.ModelViewSet):
    queryset = SalonPublication.objects.all()
    serializer_class = SalonPublicationSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        qs = SalonPublication.objects.all().select_related('salon').order_by('-created_at')
        salon_id = self.request.query_params.get('salon')
        if salon_id:
            return qs.filter(salon_id=salon_id)
        return qs

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class HairstylePublicationViewSet(viewsets.ModelViewSet):
    queryset = HairstylePublication.objects.all()
    serializer_class = HairstylePublicationSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        qs = HairstylePublication.objects.select_related('salon', 'hairdresser').prefetch_related('salon__services').order_by('-created_at')
        hairdresser_id = self.request.query_params.get('hairdresser')
        if hairdresser_id:
            qs = qs.filter(hairdresser_id=hairdresser_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(hairdresser=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(hairdresser=self.request.user)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        salon_id = self.request.query_params.get('salon')
        if salon_id:
            return self.queryset.filter(salon_id=salon_id)
        return self.queryset

    def perform_create(self, serializer):
        appointment_id = self.request.data.get('appointment')
        extra_kwargs = {'client': self.request.user}
        if appointment_id:
            extra_kwargs['appointment_id'] = appointment_id
        serializer.save(**extra_kwargs)
