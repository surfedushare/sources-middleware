from django.contrib import admin

from testing.models import ManualPerson, ManualProject


class ManualEntityAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at", "modified_at",)


admin.site.register(ManualPerson, ManualEntityAdmin)
admin.site.register(ManualProject, ManualEntityAdmin)
