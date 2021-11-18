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

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def is_allowed(self, entity, update=False):
        return entity in self.entities and \
               self.entities[entity]["is_available"] and \
               (not update or self.entities[entity]["allows_update"])


class SourceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Source
        fields = ("name", "slug", "entities", "created_at", "modified_at",)
