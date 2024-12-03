# Notes:

# auto_now_add=True for timestamp to auto-set the creation time.
# editable=False to prevent user edits.
# ManyToManyField for tags to allow multiple tags per task.
# Custom validation can be added in the model's clean method if needed.



from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Task(models.Model):
    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('WORKING', 'Working'),
        ('PENDING REVIEW', 'Pending Review'),
        ('COMPLETED', 'Completed'),
        ('OVERDUE', 'Overdue'),
        ('CANCELLED', 'Cancelled'),
    ]

    timestamp = models.DateTimeField(auto_now_add=True, editable=False)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)
    due_date = models.DateTimeField(null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='OPEN')

    def __str__(self):
        return self.title
    
    def clean(self):
        super().clean()
        if self.due_date and self.due_date < timezone.now():
            raise ValidationError('Due date cannot be in the past.')
