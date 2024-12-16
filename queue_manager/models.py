from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


# Custom User Model
class CustomUser(AbstractUser):
    org_admin = 'org_admin'
    site_admin = 'site_admin'
    user = 'user'
    ROLE_CHOICES = [
        (org_admin, 'Organization Admin'),
        (site_admin, 'Site Admin'),
        (user, 'User'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=user)
    
    # Add the organization field to map org_admin to an organization
    organization = models.ForeignKey(
        'Organization', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='admins',
        limit_choices_to={'org_type': 'org_admin'}
    )

    def __str__(self):
        return self.username


# Organization Model
class Organization(models.Model):
    name = models.CharField(max_length=255)
    org_type = models.CharField(max_length=100)
    location = models.CharField(max_length=255)  # You can use a GeoDjango model for coordinates
    about = models.TextField()

    def __str__(self):
        return self.name


# Line Model
class Line(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('open', 'Open'),
        ('closed', 'Closed'),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='queues')
    name = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField()
    date = models.DateField()
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='scheduled')

    def __str__(self):
        return f"{self.name} ({self.organization.name})"

    def update_status(self):
        current_time = timezone.now().time()
        if self.date < timezone.now().date() or (self.date == timezone.now().date() and current_time > self.closing_time):
            self.status = 'closed'
        elif self.date == timezone.now().date() and self.opening_time <= current_time <= self.closing_time:
            self.status = 'open'
        else:
            self.status = 'scheduled'
        self.save()


# Registration Model
class Registration(models.Model):
    queue = models.ForeignKey(Line, on_delete=models.CASCADE, related_name='registrations')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='registrations')
    full_name = models.CharField(max_length=100)
    dob = models.DateField()
    mobile_no = models.CharField(max_length=15)
    email = models.EmailField()
    aadhaar_no = models.CharField(max_length=12, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.queue.name}"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['queue', 'user'], name='unique_registration')
        ]
