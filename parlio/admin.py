from django.contrib import admin
from .models import User, Question, Notification

# Register your models here.
admin.site.register(User)
admin.site.register(Question)

# Displays timestamp in Django admin view.
class NotificationAdmin(admin.ModelAdmin):
    readonly_fields = ('timestamp',)
admin.site.register(Notification, NotificationAdmin)