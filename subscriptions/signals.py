from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Subscription
from .services import create_initial_payment


@receiver(post_save, sender=Subscription)
def create_first_payment(sender, instance, created, **kwargs):
    if created:
        create_initial_payment(instance)
