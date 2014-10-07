from django.contrib import admin
import models


class PostAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('title',)}

admin.site.register(models.Post, PostAdmin)
