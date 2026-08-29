from django.db import models
from django.conf import settings

class Salon(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    address = models.CharField(max_length=300)
    phone_number = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    video_url = models.URLField(max_length=500, blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='managed_salons'
    )
    hairdressers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='working_at_salons',
        limit_choices_to={'role': 'hairdresser'},
        blank=True
    )
    subscription_active_until = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name

class Service(models.Model):
    CATEGORY_CHOICES = (
        ('hair', 'Coiffure'),
        ('nails', 'Ongles'),
        ('piercing', 'Piercing'),
        ('makeup', 'Makeup'),
        ('skincare', 'Soins'),
    )
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.PositiveIntegerField(help_text="Duration in minutes")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='hair')

    def __str__(self):
        return f"{self.name} - {self.salon.name} ({self.price} FCFA)"

CATEGORY_CHOICES = (
    ('hair', 'Hairstyle'),
    ('nails', 'Nails'),
    ('piercing', 'Piercing'),
    ('makeup', 'Makeup'),
    ('skincare', 'Skincare'),
)

class SalonPublication(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='publications')
    title = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='hair')
    media = models.FileField(upload_to='publications/', blank=True, null=True)
    media_url = models.URLField(max_length=500, blank=True, null=True)
    media_type = models.CharField(
        max_length=10,
        choices=(('image', 'Image'), ('video', 'Video')),
        default='image'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Publication: {self.title or 'Untitled'} for {self.salon.name}"

class HairstylePublication(models.Model):
    hairdresser = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='hairstyles'
    )
    salon = models.ForeignKey(
        'Salon',
        on_delete=models.CASCADE,
        related_name='hairstyle_publications',
        null=True,
        blank=True
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='hair')
    media = models.FileField(upload_to='hairstyles/', blank=True, null=True)
    media_url = models.URLField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} by {self.hairdresser.username}"

class Review(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='reviews')
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    appointment = models.OneToOneField(
        'appointments.Appointment',
        on_delete=models.CASCADE,
        related_name='review',
        null=True,
        blank=True
    )
    rating = models.PositiveIntegerField(default=5)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.salon.name} by {self.client.username} ({self.rating}/5)"

class SubscriptionTransaction(models.Model):
    TRANSACTION_TYPES = (
        ('trial', 'Free Trial'),
        ('subscription', 'Subscription Payment'),
    )
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='subscription_transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    operator = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=50, blank=True)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, default='subscription')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.salon.name} - {self.amount} FCFA ({self.transaction_type})"
