from django import forms
from .models import Member, Interest

class MembershipApplicationForm(forms.ModelForm):
    interests = forms.ModelMultipleChoiceField(
        queryset=Interest.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    agree_terms = forms.BooleanField(required=True)

    class Meta:
        model = Member
        fields = [
            'first_name', 'last_name', 'email', 'phone_number', 'location',
            'interests', 'professional_background', 'why_join', 'how_contribute'
        ]
