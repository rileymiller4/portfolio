from django.contrib import admin
from .models import Skill, Review, BookingRequest

# ...existing code...

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("skill", "reviewer", "rating", "created_at")
    search_fields = ("skill__title", "reviewer__username")


@admin.register(BookingRequest)
class BookingRequestAdmin(admin.ModelAdmin):
    list_display = ('skill', 'requester', 'status', 'slot', 'created_at')
    list_filter = ("status",)
    search_fields = ("skill__title", "requester__username")