from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q

from account.models import Profile, Contact
from account.apps import AccountConfig
from images.models import Image
from images.apps import ImagesConfig


CONTENT_TYPE_CHOICES = (
    Q(app_label=ImagesConfig.name, model=Image.__name__.lower())
    | Q(app_label=AccountConfig.name, model=Profile.__name__.lower())
    | Q(app_label=AccountConfig.name, model=Contact.__name__.lower())
)


class Action(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='actions',
        on_delete=models.CASCADE
    )
    verb = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    target_ct = models.ForeignKey(
        ContentType,
        blank=True,
        null=True,
        related_name='targe_obj',
        on_delete=models.CASCADE,
        limit_choices_to=CONTENT_TYPE_CHOICES
    )
    target_id = models.PositiveIntegerField(null=True, blank=True)
    target = GenericForeignKey('target_ct', 'target_id')

    class Meta:
        indexes = [
            models.Index(fields=['-created']),
            models.Index(fields=['target_ct', 'target_id'])
        ]
        ordering = ['-created']
