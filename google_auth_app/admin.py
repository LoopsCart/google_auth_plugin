from django.contrib import admin

from .models import GoogleCredential


@admin.register(GoogleCredential)
class GoogleCredentialAdmin(admin.ModelAdmin):
    list_display = ("client_id",)

    # Optional: Prevent adding more than one via admin
    def has_add_permission(self, request):
        return not GoogleCredential.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Allow deletion if it's the only one
        if obj and GoogleCredential.objects.count() == 1:
            return True
        return False
