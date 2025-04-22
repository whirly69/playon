from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import User

class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Username')
    password = forms.CharField(widget=forms.PasswordInput, label='Password')

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label='Password')

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'birth_date', 'phone', 'role', 'player_role','password']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'username': 'Username',
            'first_name': 'Nome',
            'last_name': 'Cognome',
            'email': 'Email',
            'birth_date': 'Data di nascita',
            'phone': 'Telefono',
            'role': 'Funzione (es. Giocatore)',
            'player_role': 'Ruolo in campo (es. Difensore)',
        }