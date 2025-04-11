from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class Auction(models.Model):
    artwork = models.OneToOneField('artworks.Artwork', on_delete=models.CASCADE, related_name='auction')
    starting_price = models.DecimalField(_('Prezzo Iniziale'), max_digits=10, decimal_places=2)
    current_price = models.DecimalField(_('Prezzo Attuale'), max_digits=10, decimal_places=2)
    highest_bidder = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='won_auctions')
    start_time = models.DateTimeField(_('Ora Inizio'), default=timezone.now)
    end_time = models.DateTimeField(_('Ora Fine'), default=timezone.now)
    last_bid_time = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(_('Attiva'), default=True)
    is_live = models.BooleanField(_('In Diretta'), default=False)
    live_stream = models.ForeignKey('live_streams.LiveStream', on_delete=models.SET_NULL, null=True, blank=True, related_name='auctions')
    min_bid_increment = models.DecimalField(_('Incremento Minimo'), max_digits=10, decimal_places=2, default=1.00)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Asta')
        verbose_name_plural = _('Aste')
        ordering = ['-created_at']

    def __str__(self):
        return f"Asta per {self.artwork.title}"

    def place_bid(self, user, amount):
        if not self.is_active:
            return False, "Asta non attiva"
        
        if amount <= self.current_price:
            return False, "Offerta troppo bassa"
        
        if amount < self.current_price + self.min_bid_increment:
            return False, f"Offerta deve essere almeno {self.min_bid_increment}€ superiore"
        
        self.current_price = amount
        self.highest_bidder = user
        self.last_bid_time = timezone.now()
        self.save()
        
        return True, "Offerta accettata"

    def end_auction(self):
        if self.is_active:
            self.is_active = False
            if self.highest_bidder:
                self.artwork.mark_as_sold(self.highest_bidder, self.current_price)
            self.save()

    def extend_time(self, minutes):
        if self.is_active:
            self.end_time += timezone.timedelta(minutes=minutes)
            self.save()
            return True
        return False

    @property
    def time_remaining(self):
        if not self.is_active:
            return None
        return self.end_time - timezone.now()

    @property
    def is_ended(self):
        return not self.is_active or timezone.now() > self.end_time

    @property
    def is_about_to_end(self):
        if not self.is_active:
            return False
        return self.time_remaining.total_seconds() <= 300  # 5 minuti
