from django.db import models
from users.models import User
from projects.models import Project
from django.contrib.auth import get_user_model
User = get_user_model()

class Task(models.Model):
    STATUS_TASK = [
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('pending_approval', 'Pending Approval'),
        ('returned', 'Returned for Rework'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
       # ('done', 'Done'),
    ]
    STATUS_CHOICES = [
        ('no_done', 'No Done'),
        ('done', 'Done'),
    ]


    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_TASK, default='todo')
    normal_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='no_done')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    assigned_to = models.ManyToManyField(User, related_name='tasks', blank=True)

    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)


    def __str__(self):
        return self.title
