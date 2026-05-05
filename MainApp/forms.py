from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Skill, Review, BookingRequest, UserReview


class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = [
            'title', 'description', 'category', 'is_free', 'price',
            'contact_preference', 'availability_status'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name == 'is_free':
                field.widget.attrs['class'] = 'form-check-input'
            elif 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get('is_free') and not cleaned.get('price'):
            raise forms.ValidationError('Enter a price or mark this as free.')
        if cleaned.get('is_free'):
            cleaned['price'] = None
        return cleaned


class StudentRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-select'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class UserReviewForm(forms.ModelForm):
    rating = forms.TypedChoiceField(
        choices=[(i, str(i)) for i in range(1, 6)],
        coerce=int,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    class Meta:
        model = UserReview
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Write your review here...'}),
        }

class BookingRequestForm(forms.ModelForm):
    class Meta:
        model = BookingRequest
        fields = ['slot']
        widgets = {
            'slot': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        skill = kwargs.pop('skill', None)
        super().__init__(*args, **kwargs)
        if skill is not None:
            from .models import AvailabilitySlot
            from datetime import date, timedelta
            thirty_days_from_now = date.today() + timedelta(days=30)
            
            self.fields['slot'].queryset = AvailabilitySlot.objects.filter(
                user=skill.owner, 
                is_booked=False,
                date__gte=date.today(),
                date__lte=thirty_days_from_now
            ).order_by('date', 'start_time')
            self.fields['slot'].empty_label = "Select an available time"
        else:
            self.fields['slot'].queryset = BookingRequest.objects.none()