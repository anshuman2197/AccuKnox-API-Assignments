from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, validators=[validate_email])

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  

    def save(self, *args, **kwargs):
        self.email = self.email.lower()
        if '@' not in self.email:
            raise ValidationError("Email must contain '@'.")
        super(CustomUser, self).save(*args, **kwargs)

    def __str__(self):
        return self.email


    

class FriendRequest(models.Model):
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_friend_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_friend_requests', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=(('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')), default='pending')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_user', 'to_user')