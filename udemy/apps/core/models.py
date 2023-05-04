from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class TimeStampedBase(models.Model):
    """
    Este modelo é utilizado como base para outros modelos que necessitem armazenar informações
    de data e hora de criação e modificação.
    """

    created = models.DateTimeField(
        _('Creation Date and Time'),
        auto_now_add=True,
    )

    modified = models.DateTimeField(
        _('Modification Date and Time'),
        auto_now=True,
    )

    class Meta:
        abstract = True


class CreatorBase(models.Model):
    """
    Este modelo é utilzado para definir um criador de um objeto que é definido automáticamente
    através de um middleware.
    """

    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('creator'),
        editable=False,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        from udemy.apps.core.middleware import get_current_user

        if not self.creator:
            self.creator = get_current_user()
        super().save(*args, **kwargs)

    save.alters_data = True


class ContentBase(models.Model):
    """
    Este modelo fornece os atributos de título, descrição e status de publicação para outros modelos.
    """

    title = models.CharField(_('Title'), max_length=256)
    description = models.TextField(_('Description'))
    is_published = models.BooleanField(_('Is Published'), default=False)

    class Meta:
        abstract = True
