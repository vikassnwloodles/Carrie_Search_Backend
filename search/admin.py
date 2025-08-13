

from django.contrib import admin
from .models import UserProfile,SearchQuery, SharedChat
admin.site.register(UserProfile)
admin.site.register(SearchQuery)
admin.site.register(SharedChat)

