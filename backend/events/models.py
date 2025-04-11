from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class Event(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', _('Bozza')
        PUBLISHED = 'published', _('Pubblicato')
        CANCELLED = 'cancelled', _('Cancellato')
        COMPLETED = 'completed', _('Completato')

    name = models.CharField(_('Nome Evento'), max_length=200)
    description = models.TextField(_('Descrizione'))
    date = models.DateTimeField(_('Data e Ora'))
    location = models.CharField(_('Luogo'), max_length=200)
    address = models.TextField(_('Indirizzo'))
    city = models.CharField(_('Città'), max_length=100)
    country = models.CharField(_('Paese'), max_length=100)
    
    # Media e promozione
    cover_image = models.ImageField(_('Immagine Copertina'), upload_to='events/covers/')
    promo_video = models.URLField(_('Video Promo'), blank=True)
    gallery = models.ManyToManyField('media.Media', blank=True, related_name='events')
    
    # Organizzazione
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_events')
    artists = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='events', limit_choices_to={'role__in': ['artist', 'verified_artist']})
    promoters = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='promoted_events', limit_choices_to={'role': 'promoter'})
    
    # Configurazione
    status = models.CharField(_('Stato'), max_length=20, choices=Status.choices, default=Status.DRAFT)
    is_public = models.BooleanField(_('Pubblico'), default=True)
    max_participants = models.IntegerField(_('Max Partecipanti'), null=True, blank=True)
    ticket_price = models.DecimalField(_('Prezzo Biglietto'), max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Informazioni aggiuntive
    map_url = models.URLField(_('URL Mappa'), blank=True)
    contact_info = models.TextField(_('Info Contatto'), blank=True)
    table_booking_info = models.TextField(_('Info Prenotazione Tavoli'), blank=True)
    
    # Statistiche
    views_count = models.IntegerField(_('Visualizzazioni'), default=0)
    registered_count = models.IntegerField(_('Registrati'), default=0)
    checked_in_count = models.IntegerField(_('Check-in'), default=0)
    
    class Meta:
        verbose_name = _('Evento')
        verbose_name_plural = _('Eventi')
        ordering = ['-date']

    def __str__(self):
        return self.name

    def publish(self):
        if self.status == self.Status.DRAFT:
            self.status = self.Status.PUBLISHED
            self.save()
            return True
        return False

    def cancel(self):
        if self.status in [self.Status.DRAFT, self.Status.PUBLISHED]:
            self.status = self.Status.CANCELLED
            self.save()
            return True
        return False

    def complete(self):
        if self.status == self.Status.PUBLISHED:
            self.status = self.Status.COMPLETED
            self.save()
            return True
        return False

    @property
    def is_upcoming(self):
        return self.date > timezone.now()

    @property
    def is_full(self):
        if self.max_participants:
            return self.registered_count >= self.max_participants
        return False

    @property
    def has_available_tickets(self):
        if self.max_participants:
            return self.registered_count < self.max_participants
        return True

    def increment_views(self):
        self.views_count += 1
        self.save()

    def increment_registrations(self):
        self.registered_count += 1
        self.save()

    def increment_check_ins(self):
        self.checked_in_count += 1
        self.save()
