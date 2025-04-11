from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator
import os

class Media(models.Model):
    class Type(models.TextChoices):
        IMAGE = 'image', _('Immagine')
        VIDEO = 'video', _('Video')
        AUDIO = 'audio', _('Audio')
        DOCUMENT = 'document', _('Documento')

    class Status(models.TextChoices):
        PROCESSING = 'processing', _('In Elaborazione')
        READY = 'ready', _('Pronto')
        ERROR = 'error', _('Errore')

    title = models.CharField(_('Titolo'), max_length=200)
    description = models.TextField(_('Descrizione'), blank=True)
    file = models.FileField(
        _('File'),
        upload_to='media/',
        validators=[
            FileExtensionValidator(
                allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'mp4', 'webm', 'mp3', 'wav', 'pdf', 'doc', 'docx']
            )
        ]
    )
    type = models.CharField(_('Tipo'), max_length=20, choices=Type.choices)
    status = models.CharField(_('Stato'), max_length=20, choices=Status.choices, default=Status.PROCESSING)
    
    # Metadati
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='media')
    uploaded_at = models.DateTimeField(_('Caricato il'), auto_now_add=True)
    file_size = models.IntegerField(_('Dimensione File'), help_text=_('Dimensione in bytes'))
    duration = models.DurationField(_('Durata'), null=True, blank=True, help_text=_('Per video/audio'))
    width = models.IntegerField(_('Larghezza'), null=True, blank=True, help_text=_('Per immagini/video'))
    height = models.IntegerField(_('Altezza'), null=True, blank=True, help_text=_('Per immagini/video'))
    
    # Thumbnails e preview
    thumbnail = models.ImageField(_('Thumbnail'), upload_to='media/thumbnails/', null=True, blank=True)
    preview_url = models.URLField(_('URL Preview'), blank=True)
    
    # Privacy e accesso
    is_public = models.BooleanField(_('Pubblico'), default=True)
    access_token = models.CharField(_('Token Accesso'), max_length=100, blank=True)
    
    class Meta:
        verbose_name = _('Media')
        verbose_name_plural = _('Media')
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.file_size and self.file:
            self.file_size = self.file.size
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Rimuovi i file fisici
        if self.file:
            if os.path.isfile(self.file.path):
                os.remove(self.file.path)
        if self.thumbnail:
            if os.path.isfile(self.thumbnail.path):
                os.remove(self.thumbnail.path)
        super().delete(*args, **kwargs)

    @property
    def file_extension(self):
        return os.path.splitext(self.file.name)[1].lower()

    @property
    def is_image(self):
        return self.type == self.Type.IMAGE

    @property
    def is_video(self):
        return self.type == self.Type.VIDEO

    @property
    def is_audio(self):
        return self.type == self.Type.AUDIO

    @property
    def is_document(self):
        return self.type == self.Type.DOCUMENT

    @property
    def file_size_formatted(self):
        """Restituisce la dimensione del file formattata"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if self.file_size < 1024:
                return f"{self.file_size:.2f} {unit}"
            self.file_size /= 1024
        return f"{self.file_size:.2f} TB"
