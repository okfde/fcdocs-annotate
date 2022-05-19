from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from filingcabinet import get_document_model

Document = get_document_model()


@receiver(post_save, sender=Document)
def publish_document(sender, instance, created, **kwargs):
    publish_setting = getattr(settings, "FCDOCS_ANNOTATE_PUBLISH_DOCUMENTS", False)
    if created and not instance.public and publish_setting:
        instance.public = True
        instance.save
