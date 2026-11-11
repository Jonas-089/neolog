from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile


# creating profile for each new user
@receiver(signal=post_save, sender=User)
def create_profile(sender, instance, created, raw=False, **kwargs):
    # raw: objects loaded from a fixture (loaddata) already bring their profile
    if created and not raw:
        Profile.objects.create(user=instance)


@receiver(signal=post_save, sender=User)
def save_profile(sender, instance, created, raw=False, **kwargs):
    if not raw:
        instance.profile.save()
