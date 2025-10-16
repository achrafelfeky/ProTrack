from django.db import models
from django.conf import settings  
from django.contrib.auth import get_user_model
User = get_user_model()

#-----------------------------
class Project(models.Model):
        STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
    ]
        PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]


        name = models.CharField(max_length=100)
        description = models.TextField(blank=True)
        owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_projects'
    )
        created_at = models.DateTimeField(auto_now_add=True)
        due_date = models.DateField(null=True, blank=True)
        status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
        priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
        assigned_to = models.ManyToManyField(User, related_name='project', blank=True)
        current_time_for_check = models.DateTimeField(null=True, blank=True)

        def __str__(self):
          return self.name
