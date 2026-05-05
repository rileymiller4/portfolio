from django.contrib import admin

from .models import AboutPage, ContactMessage, SkillsPage


@admin.register(AboutPage)
class AboutPageAdmin(admin.ModelAdmin):
	list_display = ('title', 'updated_at')
	search_fields = ('title', 'intro', 'story_text', 'bring_points')


@admin.register(SkillsPage)
class SkillsPageAdmin(admin.ModelAdmin):
	list_display = ('title', 'updated_at')
	search_fields = ('title', 'intro', 'skills_text', 'tip_text')


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
	list_display = ('created_at', 'name', 'email', 'subject')
	search_fields = ('name', 'email', 'subject', 'message')
