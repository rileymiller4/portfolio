import random
from decimal import Decimal
from django.contrib.auth.models import User


from django.db import models

# Skill model

class Skill(models.Model):
    CATEGORY_CHOICES = [
        ("academics", "Academics"),
        ("tech", "Tech"),
        ("creative", "Creative"),
        ("wellness", "Wellness"),
        ("other", "Other"),
    ]
    AVAILABILITY_CHOICES = [
        ("available", "Available"),
        ("busy", "Busy"),
        ("scheduled", "Scheduled"),
    ]
    CONTACT_CHOICES = [
        ("email", "Email"),
        ("phone", "Phone"),
    ]
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='skills')
    title = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    is_free = models.BooleanField(default=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    contact_preference = models.CharField(max_length=20, choices=CONTACT_CHOICES)
    availability_status = models.CharField(max_length=20, choices=AVAILABILITY_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def avg_rating(self):
        """Calculate the average rating for a skill."""
        reviews = self.reviews.all()
        if not reviews:
            return 0
        return sum(r.rating for r in reviews) / len(reviews)

    def __str__(self):
        return self.title

# Review model
class Review(models.Model):
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.skill} - {self.reviewer}"

class AvailabilitySlot(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='availability_slots')
    date = models.DateField()
    start_time = models.TimeField()
    is_booked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.date.strftime('%b %d, %Y')} at {self.start_time.strftime('%I:%M %p')}"

# BookingRequest model
class BookingRequest(models.Model):
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='booking_requests')
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='booking_requests')
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("denied", "Denied"),
        ("completed", "Completed"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    slot = models.ForeignKey(AvailabilitySlot, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.skill} - {self.requester}"

# UserReview model for reviewing other users directly
class UserReview(models.Model):
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_user_reviews')
    reviewee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_user_reviews')
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.reviewer} -> {self.reviewee}"

NUM_USERS = 20
NUM_SKILLS = 60

categories = ["academics", "tech", "creative", "wellness", "other"]
prefs = ["email", "phone", "chat"]
statuses = ["available", "busy", "scheduled"]
topics = [
    "Math Tutoring", "Python Help", "Cooking Basics", "Resume Review",
    "Chemistry Support", "Guitar Lessons", "Graphic Design", "Public Speaking",
    "Essay Editing", "Excel Help"
]

