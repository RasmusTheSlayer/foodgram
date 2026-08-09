from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """
    Админ панель для модели User
    с поиском по username и email
    """

    list_display = ('username', 'email', 'first_name', 'last_name')
    search_fields = ('email', 'username')
    ordering = ('id',)
