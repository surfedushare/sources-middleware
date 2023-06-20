from django.db import models
from django.conf import settings
from rest_framework import serializers


def get_entities_default():
    return {
        entity: {
            "is_available": False,
            "allows_update": False
        }
        for entity in settings.ENTITIES
    }


class Source(models.Model):

    name = models.CharField(max_length=50)
    slug = models.SlugField()
    entities = models.JSONField(default=get_entities_default)
    is_repository = models.BooleanField(
        default=False,
        help_text="Enable when source is a repository for multiple organizations"
    )
    proxy_files = models.BooleanField(
        default=False,
        help_text="Enable when the source need to proxy files to circumvent authentication during file downloads"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def is_allowed(self, entity, update=False):
        if entity == "files":
            return self.proxy_files
        return entity in self.entities and \
            self.entities[entity]["is_available"] and \
            (not update or self.entities[entity]["allows_update"])


class SourceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Source
        fields = ("name", "slug", "entities", "is_repository", "created_at", "modified_at",)
