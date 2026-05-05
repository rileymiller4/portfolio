from django.contrib import admin

from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
	list_display = ('title', 'slug', 'updated_at')
	search_fields = ('title', 'one_sentence_summary', 'business_problem', 'tools_used')
	prepopulated_fields = {'slug': ('title',)}
