from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import User

class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Username')
    password = forms.CharField(widget=forms.PasswordInput, label='Password')
    
class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label='Password')
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    receive_emails = forms.BooleanField(required=False, initial=True, label="Desidero ricevere email da PlayOn")
    receive_whatsapp = forms.BooleanField(required=False, initial=False, label="Desidero ricevere messaggi WhatsApp")
    birth_date = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Data di nascita"
    )
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

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('password') != cleaned_data.get('confirm_password'):
            raise forms.ValidationError("Le password non coincidono.")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.receive_emails = self.cleaned_data['receive_emails']
        user.receive_whatsapp = self.cleaned_data['receive_whatsapp']
        if commit:
            user.save()
        return user
    
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'birth_date', 'player_role', 'receive_emails', 'receive_whatsapp']
    
    receive_emails = forms.BooleanField(required=False, label="Ricevi email da PlayOn")
    receive_whatsapp = forms.BooleanField(required=False, label="Ricevi messaggi WhatsApp (in futuro)")
