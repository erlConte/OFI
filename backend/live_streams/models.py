from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class LiveStream(models.Model):
    class Status(models.TextChoices):
        SCHEDULED = 'scheduled', _('Programmata')
        LIVE = 'live', _('In Diretta')
        ENDED = 'ended', _('Conclusa')
        CANCELLED = 'cancelled', _('Cancellata')

    title = models.CharField(_('Titolo'), max_length=200)
    description = models.TextField(_('Descrizione'), blank=True)
    artist = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='live_streams')
    artwork = models.ForeignKey('artworks.Artwork', on_delete=models.SET_NULL, null=True, blank=True, related_name='live_streams')
    event = models.ForeignKey('events.Event', on_delete=models.SET_NULL, null=True, blank=True, related_name='live_streams')
    
    status = models.CharField(_('Stato'), max_length=20, choices=Status.choices, default=Status.SCHEDULED)
    scheduled_start = models.DateTimeField(_('Inizio Programmato'))
    started_at = models.DateTimeField(_('Inizio Effettivo'), null=True, blank=True)
    ended_at = models.DateTimeField(_('Fine'), null=True, blank=True)
    
    # URL e configurazione streaming
    stream_url = models.URLField(_('URL Stream'), blank=True)
    stream_key = models.CharField(_('Chiave Stream'), max_length=100, blank=True)
    video_url = models.URLField(_('URL Replay'), blank=True)
    
    # Statistiche
    viewers_count = models.IntegerField(_('Numero Spettatori'), default=0)
    peak_viewers = models.IntegerField(_('Picco Spettatori'), default=0)
    duration = models.DurationField(_('Durata'), null=True, blank=True)
    
    # Configurazione
    is_public = models.BooleanField(_('Pubblica'), default=True)
    allow_chat = models.BooleanField(_('Chat Attiva'), default=True)
    allow_comments = models.BooleanField(_('Commenti Attivi'), default=True)
    
    class Meta:
        verbose_name = _('Live Stream')
        verbose_name_plural = _('Live Streams')
        ordering = ['-scheduled_start']

    def __str__(self):
        return f"{self.title} - {self.artist.username}"

    def start(self):
        if self.status == self.Status.SCHEDULED:
            self.status = self.Status.LIVE
            self.started_at = timezone.now()
            self.save()

    def end(self):
        if self.status == self.Status.LIVE:
            self.status = self.Status.ENDED
            self.ended_at = timezone.now()
            if self.started_at:
                self.duration = self.ended_at - self.started_at
            self.save()

    def cancel(self):
        if self.status in [self.Status.SCHEDULED, self.Status.LIVE]:
            self.status = self.Status.CANCELLED
            self.save()

    @property
    def is_active(self):
        return self.status == self.Status.LIVE

    @property
    def has_replay(self):
        return bool(self.video_url)

    def update_viewers(self, count):
        self.viewers_count = count
        if count > self.peak_viewers:
            self.peak_viewers = count
        self.save()
