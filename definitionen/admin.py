from django.contrib import admin
from .models import Definition, Word


# to show all definitions to a word in the admin section
# taken from: https://stackoverflow.com/questions/21657225/how-to-show-related-objects-in-django-admin
class DefinitionInLine(admin.TabularInline):
    model = Definition


class WordAdmin(admin.ModelAdmin):
    inlines = [
        DefinitionInLine,
    ]


class DefinitionAdmin(admin.ModelAdmin):
    list_display = ("title", "word", "author", "date_posted", "ai_generated")
    list_filter = ("ai_generated",)


admin.site.register(Definition, DefinitionAdmin)
admin.site.register(Word, WordAdmin)