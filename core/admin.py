from django.contrib import admin

from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_email', 'avatar', 'avatar_color', 'created_at', )
    list_filter = ('avatar_color', 'created_at', )
    search_fields = ('user__username', 'user__email')
    list_select_related = ('user',)

    @admin.display(description='Электронная почта', ordering='user__email')
    def user_email(self, profile: Profile) -> str:
        return profile.user.email
