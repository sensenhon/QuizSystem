from django.db import models
from django_ckeditor_5.fields import CKEditor5Field

# Create your models here.
class Message(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username}, {self.subject}"
    
class Blog(models.Model):
    title = models.CharField(max_length=255)
    content = CKEditor5Field('Text', config_name='extends')
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    STATUS = (
        ('public', 'Public'),
        ('private', 'Private'),
    )
    status = models.CharField(max_length=255, choices=STATUS)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title