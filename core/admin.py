from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .models import Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    extra = 0
    max_num = 1


User = get_user_model()
admin.site.unregister(User)


@admin.register(User)
class UserWithProfileAdmin(UserAdmin):
    inlines = (ProfileInline,)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    autocomplete_fields = ('user',)
    list_display = ('user', 'user_email', 'avatar', 'avatar_color', 'created_at', )
    list_filter = ('avatar_color', 'created_at', )
    search_fields = ('user__username', 'user__email')
    list_select_related = ('user',)

    @admin.display(description='Электронная почта', ordering='user__email')
    def user_email(self, profile: Profile) -> str:
        return profile.user.email
