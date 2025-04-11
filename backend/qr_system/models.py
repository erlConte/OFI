from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import uuid

class EventRegistration(models.Model):
    event = models.ForeignKey('events.Event', on_delete=models.CASCADE, related_name='registrations')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='event_registrations')
    qr_code = models.UUIDField(_('QR Code'), default=uuid.uuid4, editable=False, unique=True)
    checked_in = models.BooleanField(_('Check-in Effettuato'), default=False)
    checked_in_at = models.DateTimeField(null=True, blank=True)
    scanned_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='scanned_registrations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Registrazione Evento')
        verbose_name_plural = _('Registrazioni Eventi')
        unique_together = ['event', 'user']
        ordering = ['-created_at']

    def __str__(self):
        return f"Registrazione {self.event.name} - {self.user.username if self.user else 'Guest'}"

    def check_in(self, scanner):
        if not self.checked_in:
            self.checked_in = True
            self.checked_in_at = timezone.now()
            self.scanned_by = scanner
            self.save()
            return True
        return False

    @property
    def is_valid(self):
        return not self.checked_in and self.event.is_active and not self.event.is_past

    @property
    def qr_data(self):
        return {
            'registration_id': str(self.qr_code),
            'event_name': self.event.name,
            'event_date': self.event.date.isoformat(),
            'user_name': self.user.username if self.user else 'Guest'
        }
