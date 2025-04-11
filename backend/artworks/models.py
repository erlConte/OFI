from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class Artwork(models.Model):
    title = models.CharField(_('Titolo'), max_length=200)
    description = models.TextField(_('Descrizione'))
    image = models.ImageField(_('Immagine'), upload_to='artworks/')
    price = models.DecimalField(_('Prezzo'), max_digits=10, decimal_places=2)
    is_digital = models.BooleanField(_('È digitale'), default=False)
    blockchain_hash = models.CharField(_('Hash Blockchain'), max_length=66, blank=True, null=True)
    artist = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='artworks')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_for_auction = models.BooleanField(_('In asta'), default=False)
    is_sold = models.BooleanField(_('Venduto'), default=False)
    sold_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='purchased_artworks')
    sold_at = models.DateTimeField(null=True, blank=True)
    views_count = models.PositiveIntegerField(_('Visualizzazioni'), default=0)
    likes_count = models.PositiveIntegerField(_('Mi piace'), default=0)
    is_verified = models.BooleanField(_('Verificato'), default=False)
    verification_date = models.DateTimeField(null=True, blank=True)
    verification_notes = models.TextField(blank=True)
    
    # Dati aggiuntivi rilevati automaticamente
    dimensions = models.CharField(_('Dimensioni'), max_length=100, blank=True, null=True)
    creation_date = models.DateField(_('Data Creazione Opera'), null=True, blank=True)
    location = models.CharField(_('Luogo'), max_length=200, blank=True, null=True)
    
    class Meta:
        verbose_name = _('Opera')
        verbose_name_plural = _('Opere')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.artist.username}"

    def increment_views(self):
        self.views_count += 1
        self.save()

    def increment_likes(self):
        self.likes_count += 1
        self.save()

    def mark_as_sold(self, buyer, price=None):
        self.is_sold = True
        self.sold_to = buyer
        self.sold_at = timezone.now()
        if price:
            self.price = price
        self.save()

    def verify(self, notes=''):
        self.is_verified = True
        self.verification_date = timezone.now()
        self.verification_notes = notes
        self.save()

    def save(self, *args, **kwargs):
        if self.is_digital and not self.blockchain_hash:
            # Qui implementare la logica per generare l'hash blockchain
            pass
        super().save(*args, **kwargs)

    @property
    def is_available(self):
        return not self.is_sold and not self.is_for_auction
