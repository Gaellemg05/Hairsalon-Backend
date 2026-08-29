from datetime import datetime, date, time, timedelta
from django.db.models import Q
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Availability, Appointment, Chat, Message
from .serializers import (
    AvailabilitySerializer, AppointmentSerializer,
    ChatSerializer, MessageSerializer
)
from salons.models import Service, Salon

class AvailabilityViewSet(viewsets.ModelViewSet):
    queryset = Availability.objects.all()
    serializer_class = AvailabilitySerializer

    def get_queryset(self):
        qs = Availability.objects.all().order_by('day_of_week', 'start_time')
        hairdresser_id = self.request.query_params.get('hairdresser')
        if hairdresser_id:
            qs = qs.filter(hairdresser_id=hairdresser_id)
        return qs

    def perform_create(self, serializer):
        start_time = serializer.validated_data.get('start_time')
        end_time = serializer.validated_data.get('end_time')
        if start_time and end_time and start_time >= end_time:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({'error': 'Start time must be before end time.'})

        if 'hairdresser' in self.request.data and self.request.user.role in ['admin', 'hairdresser']:
            serializer.save()
        else:
            serializer.save(hairdresser=self.request.user)

    @action(detail=False, methods=['post'])
    def bulk_set(self, request):
        hairdresser_id = request.data.get('hairdresser')
        slots = request.data.get('slots', [])
        if not hairdresser_id:
            return Response({'error': 'hairdresser is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Remove existing and recreate
        Availability.objects.filter(hairdresser_id=hairdresser_id).delete()
        created = []
        for slot in slots:
            day = int(slot.get('day_of_week', 0))
            st = slot.get('start_time')
            et = slot.get('end_time')
            if st and et and st < et:
                av = Availability.objects.create(
                    hairdresser_id=hairdresser_id,
                    day_of_week=day,
                    start_time=st,
                    end_time=et
                )
                created.append(av)

        serializer = AvailabilitySerializer(created, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def available_slots(self, request):
        hairdresser_id = request.query_params.get('hairdresser')
        date_str = request.query_params.get('date')
        service_id = request.query_params.get('service')

        if not hairdresser_id or not date_str:
            return Response(
                {'error': 'Both hairdresser and date query parameters are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)

        day_of_week = target_date.weekday() # 0 = Monday, 6 = Sunday
        availabilities = Availability.objects.filter(
            hairdresser_id=hairdresser_id,
            day_of_week=day_of_week
        ).order_by('start_time')

        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        day_name = day_names[day_of_week]

        if not availabilities.exists():
            return Response({
                'working': False,
                'day_name': day_name,
                'date': date_str,
                'working_hours': [],
                'slots': []
            })

        # Service duration in minutes
        duration_minutes = 30
        if service_id:
            try:
                svc = Service.objects.get(id=service_id)
                duration_minutes = max(15, svc.duration)
            except Service.DoesNotExist:
                pass

        # Existing booked appointments
        existing_appts = Appointment.objects.filter(
            hairdresser_id=hairdresser_id,
            date=target_date,
            status__in=['pending', 'confirmed']
        ).select_related('service')

        booked_ranges = []
        for appt in existing_appts:
            appt_duration = appt.service.duration if appt.service else 30
            appt_dt_start = datetime.combine(target_date, appt.time)
            appt_dt_end = appt_dt_start + timedelta(minutes=appt_duration)
            booked_ranges.append((appt_dt_start, appt_dt_end))

        now = datetime.now()
        is_today = (target_date == date.today())

        slots = []
        working_hours = []

        for av in availabilities:
            working_hours.append({
                'start': av.start_time.strftime('%H:%M'),
                'end': av.end_time.strftime('%H:%M')
            })

            curr_dt = datetime.combine(target_date, av.start_time)
            end_dt = datetime.combine(target_date, av.end_time)

            while curr_dt + timedelta(minutes=min(30, duration_minutes)) <= end_dt:
                slot_time_str = curr_dt.strftime('%H:%M')
                slot_label = curr_dt.strftime('%I:%M %p').lstrip('0')
                slot_end = curr_dt + timedelta(minutes=duration_minutes)

                is_available = True
                reason = None

                # Check past time today
                if is_today and curr_dt <= now:
                    is_available = False
                    reason = 'past'
                # Check overlapping with existing appointments
                elif any(not (slot_end <= b_start or curr_dt >= b_end) for b_start, b_end in booked_ranges):
                    is_available = False
                    reason = 'booked'

                slots.append({
                    'time': slot_time_str,
                    'label': slot_label,
                    'available': is_available,
                    'reason': reason
                })

                curr_dt += timedelta(minutes=30)

        return Response({
            'working': True,
            'day_name': day_name,
            'date': date_str,
            'working_hours': working_hours,
            'slots': slots
        })

class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return self.queryset.none()
        if user.role == 'admin':
            return self.queryset
        elif user.role == 'hairdresser':
            # Salon owners see all bookings of their salon(s) and their own bookings
            return self.queryset.filter(
                Q(hairdresser=user) | Q(salon__manager=user)
            ).distinct()
        else:
            return self.queryset.filter(client=user)

    def create(self, request, *args, **kwargs):
        data = request.data
        hairdresser_id = data.get('hairdresser')
        date_val = data.get('date')
        time_val = data.get('time')
        service_id = data.get('service')

        if not hairdresser_id or not date_val or not time_val:
            return Response(
                {'error': 'hairdresser, date, and time are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            target_date = datetime.strptime(str(date_val), '%Y-%m-%d').date()
            if isinstance(time_val, str):
                if len(time_val) == 5:
                    target_time = datetime.strptime(time_val, '%H:%M').time()
                else:
                    target_time = datetime.strptime(time_val[:8], '%H:%M:%S').time()
            else:
                target_time = time_val
        except ValueError:
            return Response(
                {'error': 'Invalid date or time format.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Date cannot be in the past
        if target_date < date.today():
            return Response(
                {'error': 'Cannot book appointments for past dates.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check stylist working availability on this day of week
        day_of_week = target_date.weekday()
        availabilities = Availability.objects.filter(
            hairdresser_id=hairdresser_id,
            day_of_week=day_of_week
        )
        if not availabilities.exists():
            return Response(
                {'error': 'The selected stylist is not scheduled to work on this day.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if time is within working hours
        is_within_hours = any(av.start_time <= target_time <= av.end_time for av in availabilities)
        if not is_within_hours:
            return Response(
                {'error': 'The selected time is outside the stylist\'s working hours.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Service duration
        duration_minutes = 30
        if service_id:
            try:
                svc = Service.objects.get(id=service_id)
                duration_minutes = max(15, svc.duration)
            except Service.DoesNotExist:
                pass

        req_dt_start = datetime.combine(target_date, target_time)
        req_dt_end = req_dt_start + timedelta(minutes=duration_minutes)

        # Check conflict with existing appointments
        existing_appts = Appointment.objects.filter(
            hairdresser_id=hairdresser_id,
            date=target_date,
            status__in=['pending', 'confirmed']
        ).select_related('service')

        for appt in existing_appts:
            appt_duration = appt.service.duration if appt.service else 30
            appt_dt_start = datetime.combine(target_date, appt.time)
            appt_dt_end = appt_dt_start + timedelta(minutes=appt_duration)
            if not (req_dt_end <= appt_dt_start or req_dt_start >= appt_dt_end):
                return Response(
                    {'error': f'This stylist already has a booking around {appt.time.strftime("%H:%M")}. Please select another time.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if self.request.user.role == 'admin' and 'client' in self.request.data:
            serializer.save()
        else:
            serializer.save(client=self.request.user)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        new_status = request.data.get('status')
        if new_status in ['confirmed', 'completed']:
            if instance.hairdresser != request.user and request.user.role != 'admin':
                return Response(
                    {'error': 'Only the assigned stylist can confirm or complete this appointment.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

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
        # Mark all messages from the other party as read
        chat.messages.filter(read=False).exclude(sender=request.user).update(read=True)
        messages = chat.messages.all()
        serializer = MessageSerializer(messages, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        chat = self.get_object()
        content = request.data.get('content', '')
        image = request.FILES.get('image')
        if not content and not image:
            return Response({'detail': 'Content or image is required.'}, status=status.HTTP_400_BAD_REQUEST)
        message = Message.objects.create(
            chat=chat,
            sender=request.user,
            content=content or '',
            image=image
        )
        serializer = MessageSerializer(message, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark all messages in this chat not sent by the current user as read."""
        chat = self.get_object()
        chat.messages.filter(read=False).exclude(sender=request.user).update(read=True)
        return Response({'status': 'ok'})

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
