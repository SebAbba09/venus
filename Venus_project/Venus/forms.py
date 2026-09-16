import re
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordResetForm, SetPasswordForm, \
    PasswordChangeForm
from .models import CustomUser, Event
from .validators import PASSWORD_VALIDATION_MSG
from django.core.exceptions import ValidationError


class CustomAuthenticationForm(AuthenticationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'password')

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        # Exemple de validation personnalisée si nécessaire
        if not username or not password:
            raise forms.ValidationError("Le nom d'utilisateur et le mot de passe ne peuvent pas être vides.")
        return cleaned_data


class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'input-box',
            'placeholder': "nom d'utilisateur"
        })
    )

    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'input-box',
            'placeholder': 'mot de passe'
        })
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'password1')


class CustomPasswordResetForm(PasswordResetForm):
    class Meta:
        model = CustomUser
        fields = ('email',)


class CustomSetPasswordForm(SetPasswordForm):
    class Meta:
        model = CustomUser
        fields = ('new_password1', 'new_password2')

    def clean_new_password1(self):
        new_password1 = self.cleaned_data.get('new_password1')
        # Validation supplémentaire pour les nouveaux mots de passe
        if new_password1 and re.match(r'^\d+$', new_password1):
            raise forms.ValidationError("Le nouveau mot de passe ne peut pas être uniquement composé de chiffres.")
        return new_password1


class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label='Ancien mot de passe',
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'}),
    )
    new_password1 = forms.CharField(
        label='Nouveau mot de passe',
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        help_text=PASSWORD_VALIDATION_MSG['min_length'],
    )
    new_password2 = forms.CharField(
        label='Confirmer le nouveau mot de passe',
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        help_text=PASSWORD_VALIDATION_MSG['min_length'],
    )

    class Meta:
        model = CustomUser
        fields = ('old_password', 'new_password1', 'new_password2')

    def clean_new_password1(self):
        new_password1 = self.cleaned_data.get('new_password1')
        # Validation supplémentaire pour les nouveaux mots de passe
        if new_password1 and re.match(r'^\d+$', new_password1):
            raise forms.ValidationError("Le nouveau mot de passe ne peut pas être uniquement composé de chiffres.")
        return new_password1


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'start_time', 'end_time']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
