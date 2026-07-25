from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


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
    default_currency = models.ForeignKey(
        'finances.Currency',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='colony_defaults',
        verbose_name='Moneda por defecto',
    )
    auto_create_debt_transactions = models.BooleanField(
        default=False,
        verbose_name='Crear gasto al pagar deuda',
    )
    auto_create_split_transactions = models.BooleanField(
        default=False,
        verbose_name='Crear gasto en splits',
    )
    budget_alert_threshold = models.IntegerField(
        default=80,
        validators=[MinValueValidator(50), MaxValueValidator(100)],
        verbose_name='Umbral de alerta de presupuesto (%)',
    )
    debt_show_days = models.IntegerField(
        default=7,
        validators=[MinValueValidator(1), MaxValueValidator(365)],
        verbose_name='Mostrar deudas con deadline en (días)',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Colonia'
        verbose_name_plural = 'Colonias'
        ordering = ['name']

    def __str__(self):
        return self.name
