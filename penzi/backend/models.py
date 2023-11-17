
from django.db import models

class User(models.Model):
    phone_number = models.CharField(max_length=15, unique=True)
    is_registered = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Check if the user is being registered for the first time
        if not self.pk and self.is_registered:
            self.is_registered = True  # Change is_registered to True for new registrations
        
        super(User, self).save(*args, **kwargs)

class ReceivedMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=10)
    county = models.CharField(max_length=100)
    town = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name}'s Profile"
    

class UserDetails(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='details')
    level_of_education = models.CharField(max_length=100)
    profession = models.CharField(max_length=100)
    marital_status = models.CharField(max_length=100)
    religion = models.CharField(max_length=100)
    ethnicity = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.user}'s Details"
    
class UserDescription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='description')
    description_text = models.TextField()


    def __str__(self):
        return f"{self.user}'s Description"