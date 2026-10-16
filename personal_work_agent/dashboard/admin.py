from django.contrib import admin
from .models import ChatMessage, UploadedDocument
admin.site.register(ChatMessage)
admin.site.register(UploadedDocument)
