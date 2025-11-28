from django.contrib import admin
from .models import Country, User, Blog, BlogView
from django.contrib.auth.models import Group
@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'country')
    list_filter = ('country',)
    search_fields = ('username',)

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at')
    list_filter = ('author', 'created_at')
    search_fields = ('title', 'author__username')
    date_hierarchy = 'created_at'

@admin.register(BlogView)
class BlogViewAdmin(admin.ModelAdmin):
    list_display = ('blog', 'viewed_at', 'count')
    list_filter = ('viewed_at',)
    search_fields = ('blog__title',)
    date_hierarchy = 'viewed_at'

admin.site.site_header = "Analytics Administration"
admin.site.unregister(Group)