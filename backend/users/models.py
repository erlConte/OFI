from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    class Role(models.TextChoices):
        GUEST = 'guest', _('Guest')
        BASE = 'base', _('Base')
        ARTIST = 'artist', _('Artista')
        VERIFIED_ARTIST = 'verified_artist', _('Artista Verificato')
        ADMIN = 'admin', _('Admin')
        PROMOTER = 'promoter', _('Promoter')

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.GUEST
    )
    bio = models.TextField(blank=True, null=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    verification_requested = models.BooleanField(default=False)
    verification_rejected = models.BooleanField(default=False)
    verification_rejection_reason = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = _('Utente')
        verbose_name_plural = _('Utenti')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_artist(self):
        return self.role in [self.Role.ARTIST, self.Role.VERIFIED_ARTIST]

    @property
    def is_verified_artist(self):
        return self.role == self.Role.VERIFIED_ARTIST

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

    @property
    def is_promoter(self):
        return self.role == self.Role.PROMOTER

    @property
    def is_base(self):
        return self.role == self.Role.BASE

class UserInteraction(models.Model):
    class ContentType(models.TextChoices):
        ARTWORK = 'artwork', _('Opera')
        EVENT = 'event', _('Evento')
        STREAM = 'stream', _('Live Stream')
        AUCTION = 'auction', _('Asta')

    class ActionType(models.TextChoices):
        VIEW = 'view', _('Visualizzazione')
        LIKE = 'like', _('Mi piace')
        BID = 'bid', _('Offerta')
        REGISTER = 'register', _('Registrazione')
        CHECK_IN = 'check_in', _('Check-in')
        COMMENT = 'comment', _('Commento')
        SHARE = 'share', _('Condivisione')

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interactions')
    content_type = models.CharField(_('Tipo Contenuto'), max_length=50, choices=ContentType.choices)
    content_id = models.IntegerField(_('ID Contenuto'))
    action = models.CharField(_('Azione'), max_length=50, choices=ActionType.choices)
    timestamp = models.DateTimeField(_('Timestamp'), auto_now_add=True)
    metadata = models.JSONField(_('Metadati'), default=dict)
    ip_address = models.GenericIPAddressField(_('Indirizzo IP'), null=True)
    user_agent = models.TextField(_('User Agent'), blank=True)

    class Meta:
        verbose_name = _('Interazione Utente')
        verbose_name_plural = _('Interazioni Utenti')
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'content_type', 'content_id']),
            models.Index(fields=['timestamp']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.get_content_type_display()} - {self.get_action_display()}"
