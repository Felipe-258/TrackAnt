from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'


class Colony(models.Model):
    name = models.CharField(max_length=200, verbose_name='Nombre')
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='owned_colonies',
        null=True,
        blank=True,
        verbose_name='Dueño',
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='colonies',
        blank=True,
        verbose_name='Miembros',
    )
    is_guest = models.BooleanField(default=False, verbose_name='Es invitado')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Colonia'
        verbose_name_plural = 'Colonias'
        ordering = ['name']

    def __str__(self):
        return self.name
