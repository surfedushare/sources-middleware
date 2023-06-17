from django.db import models

from testing.constants import PERSON_DEFAULTS, PROJECT_DEFAULTS


class ManualEntity(models.Model):

    class ManualSources(models.IntegerChoices):
        MANUAL_1 = 1
        MANUAL_2 = 2
        MANUAL_3 = 3

    name = models.CharField(max_length=100)
    source = models.IntegerField(choices=ManualSources.choices, default=ManualSources.MANUAL_1)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


def get_person_defaults():
    return PERSON_DEFAULTS


class ManualPerson(ManualEntity):
    properties = models.JSONField(default=get_person_defaults)


def get_project_defaults():
    return PROJECT_DEFAULTS


class ManualProject(ManualEntity):
    properties = models.JSONField(default=get_project_defaults)
