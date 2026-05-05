from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import SkillForm, StudentRegistrationForm, ReviewForm, BookingRequestForm, UserReviewForm
from .models import Skill, Review, BookingRequest, UserReview


class SkillSwapLoginView(LoginView):
    template_name = 'skillswap/login.html'

    def get_success_url(self):
        return reverse('skillswap:dashboard')



# ...existing code...

def home(request):
    q = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()

    skills = Skill.objects.all().order_by('-created_at')
    if q:
        skills = skills.filter(title__icontains=q)
    if category:
        skills = skills.filter(category=category)

    return render(request, 'skillswap/home.html', {
        'skills': skills,
        'q': q,
        'selected_category': category,
        'category_choices': Skill.CATEGORY_CHOICES,
    })
# ...existing code...


def skill_detail(request, pk):
    skill = get_object_or_404(Skill, pk=pk)
    has_reviewed = request.user.is_authenticated and Review.objects.filter(skill=skill, reviewer=request.user).exists()
    has_completed = request.user.is_authenticated and BookingRequest.objects.filter(
        skill=skill,
        requester=request.user,
        status='completed',
    ).exists()
    
    can_review = request.user.is_authenticated and request.user != skill.owner and not has_reviewed and has_completed
    can_book = request.user.is_authenticated and request.user != skill.owner
    
    from .models import AvailabilitySlot
    from datetime import date, timedelta
    
    thirty_days_from_now = date.today() + timedelta(days=30)
    available_slots = AvailabilitySlot.objects.filter(
        user=skill.owner, 
        is_booked=False,
        date__gte=date.today(),
        date__lte=thirty_days_from_now
    ).order_by('date', 'start_time')

    return render(request, 'skillswap/skill_detail.html', {
        'skill': skill,
        'review_form': ReviewForm(),
        'booking_form': BookingRequestForm(skill=skill),
        'can_review': can_review,
        'can_book': can_book,
        'has_booked': has_completed,
        'available_slots': available_slots,
    })


@login_required(login_url='skillswap:login')
def add_review(request, pk):
    skill = get_object_or_404(Skill, pk=pk)
    has_completed = BookingRequest.objects.filter(skill=skill, requester=request.user, status='completed').exists()
    
    if request.user == skill.owner:
        messages.error(request, 'You cannot review your own skill.')
        return redirect('skillswap:skill_detail', pk=pk)
        
    if not has_completed:
        messages.error(request, 'You can only review a skill after completing a session.')
        return redirect('skillswap:skill_detail', pk=pk)

    form = ReviewForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        review = form.save(commit=False)
        review.skill = skill
        review.reviewer = request.user
        try:
            review.save()
            messages.success(request, 'Review submitted.')
        except Exception:
            messages.error(request, 'You already reviewed this skill.')
    return redirect('skillswap:skill_detail', pk=pk)


@login_required(login_url='skillswap:login')
def create_booking(request, pk):
    skill = get_object_or_404(Skill, pk=pk)
    if request.user == skill.owner:
        messages.error(request, 'You cannot request your own skill.')
        return redirect('skillswap:skill_detail', pk=pk)

    form = BookingRequestForm(request.POST or None, skill=skill)
    if request.method == 'POST' and form.is_valid():
        booking = form.save(commit=False)
        booking.skill = skill
        booking.requester = request.user
        booking.save()
        
        # Mark slot as booked
        if booking.slot:
            booking.slot.is_booked = True
            booking.slot.save()
            
        messages.success(request, 'Booking request sent.')
    return redirect('skillswap:skill_detail', pk=pk)


@login_required(login_url='skillswap:login')
def approve_booking(request, pk):
    booking = get_object_or_404(BookingRequest, pk=pk, skill__owner=request.user)
    if request.method == 'POST':
        booking.status = 'approved'
        booking.save()
        messages.success(request, f'Session requested by {booking.requester.first_name} has been approved.')
    return redirect('skillswap:dashboard')

@login_required(login_url='skillswap:login')
def deny_booking(request, pk):
    booking = get_object_or_404(BookingRequest, pk=pk, skill__owner=request.user)
    if request.method == 'POST':
        booking.status = 'denied'
        booking.save()
        
        # Free up the slot again
        if booking.slot:
            booking.slot.is_booked = False
            booking.slot.save()
            
        messages.warning(request, f'Session requested by {booking.requester.first_name} was denied.')
    return redirect('skillswap:dashboard')

@login_required(login_url='skillswap:login')
def skill_create(request):
    if request.method == 'POST':
        form = SkillForm(request.POST)
        if form.is_valid():
            skill = form.save(commit=False)
            skill.owner = request.user
            skill.save()
            messages.success(request, 'Skill posted successfully.')
            return redirect('skillswap:skill_detail', pk=skill.pk)
    else:
        form = SkillForm()
    return render(request, 'skillswap/skill_form.html', {'form': form, 'action': 'Create Skill'})


@login_required(login_url='skillswap:login')
def skill_update(request, pk):
    skill = get_object_or_404(Skill, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = SkillForm(request.POST, instance=skill)
        if form.is_valid():
            form.save()
            messages.success(request, 'Skill updated successfully.')
            return redirect('skillswap:skill_detail', pk=skill.pk)
    else:
        form = SkillForm(instance=skill)
    return render(request, 'skillswap/skill_form.html', {'form': form, 'action': 'Edit Skill'})


@login_required(login_url='skillswap:login')
def skill_delete(request, pk):
    skill = get_object_or_404(Skill, pk=pk, owner=request.user)
    if request.method == 'POST':
        skill.delete()
        messages.success(request, 'Skill deleted.')
        return redirect('skillswap:dashboard')
    return render(request, 'skillswap/skill_confirm_delete.html', {'skill': skill})


@login_required(login_url='skillswap:login')
def complete_booking(request, pk):
    # Only owner can mark as complete
    booking = get_object_or_404(BookingRequest, pk=pk, skill__owner=request.user)
    if request.method == 'POST':
        booking.status = 'completed'
        booking.save()
        messages.success(request, f'Session with {booking.requester.first_name} marked as completed.')
    return redirect('skillswap:dashboard')

@login_required(login_url='skillswap:login')
def review_user(request, pk):
    UserModel = get_user_model()
    reviewee = get_object_or_404(UserModel, pk=pk)
    if reviewee == request.user:
        messages.error(request, 'You cannot review yourself.')
        return redirect('skillswap:dashboard')

    # Only allow reviewing if there is at least one completed session between these two users
    has_completed_together = BookingRequest.objects.filter(
        status='completed',
        skill__owner=request.user,
        requester=reviewee,
    ).exists() or BookingRequest.objects.filter(
        status='completed',
        skill__owner=reviewee,
        requester=request.user,
    ).exists()

    if not has_completed_together:
        messages.error(request, 'You can only review users after completing a session together.')
        return redirect('skillswap:dashboard')

    if UserReview.objects.filter(reviewer=request.user, reviewee=reviewee).exists():
        messages.error(request, 'You already reviewed this user.')
        return redirect('skillswap:dashboard')

    form = UserReviewForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        review = form.save(commit=False)
        review.reviewer = request.user
        review.reviewee = reviewee
        review.save()
        messages.success(request, f'Review for {reviewee.first_name} submitted successfully.')
        return redirect('skillswap:dashboard')
    
    return render(request, 'skillswap/user_review.html', {'form': form, 'reviewee': reviewee})

@login_required(login_url='skillswap:login')
def dashboard(request):
    skills = Skill.objects.filter(owner=request.user).order_by('-created_at')
    
    incoming_requests = BookingRequest.objects.filter(skill__owner=request.user).exclude(status='completed').select_related('skill', 'requester')
    my_requests = BookingRequest.objects.filter(requester=request.user).exclude(status='completed').select_related('skill')

    completed_provided = BookingRequest.objects.filter(skill__owner=request.user, status='completed').select_related('skill', 'requester')
    completed_received = BookingRequest.objects.filter(requester=request.user, status='completed').select_related('skill')

    user_reviews_given = UserReview.objects.filter(reviewer=request.user).select_related('reviewee').order_by('-created_at')
    user_reviews_received = UserReview.objects.filter(reviewee=request.user).select_related('reviewer').order_by('-created_at')

    reviewed_user_ids = list(
        UserReview.objects.filter(reviewer=request.user).values_list('reviewee_id', flat=True)
    )

    return render(request, 'skillswap/dashboard.html', {
        'skills': skills,
        'incoming_requests': incoming_requests,
        'my_requests': my_requests,
        'completed_provided': completed_provided,
        'completed_received': completed_received,
        'user_reviews_given': user_reviews_given,
        'user_reviews_received': user_reviews_received,
        'reviewed_user_ids': reviewed_user_ids,
    })


def register(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Welcome! Your account was created.')
            return redirect('skillswap:dashboard')
    else:
        form = StudentRegistrationForm()
    return render(request, 'skillswap/register.html', {'form': form})