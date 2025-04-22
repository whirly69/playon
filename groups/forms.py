from django import forms
from .models import Group, Player, Role, GroupJoinRequest

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name']

class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ['name', 'birth_date', 'role']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date','class': 'form-control'}),
        }
        labels = {
            'name': 'Nome',
            'birth_date': 'Data di nascita',
            'role': 'Ruolo in campo',
        }
        
    def __init__(self, *args, **kwargs):
        group_id = kwargs.pop("group_id", None)  # riceve group_id dal view
        super().__init__(*args, **kwargs)
        # aggiungi ID dinamico al campo ruolo per collegarlo allo script JS
        if group_id is not None:
            self.fields['role'].widget.attrs.update({
                'id': f'select-role-{group_id}'
            })
            # ⬇️ aggiungi il queryset per i ruoli relativi al gruppo
            self.fields['role'].queryset = Role.objects.filter(group_id=group_id)
        # Precompila la data di nascita se presente
        if self.instance and self.instance.birth_date:
            self.initial['birth_date'] = self.instance.birth_date.strftime('%Y-%m-%d')

class JoinRequestForm(forms.ModelForm):
    class Meta:
        model = GroupJoinRequest
        fields = []

class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome ruolo',
                'hx-post': '',  # può essere usato in futuro per aggiornamento dinamico
                'hx-trigger': 'change'
            })
        }

    def __init__(self, *args, **kwargs):
        group = kwargs.pop('group', None)
        super().__init__(*args, **kwargs)
        self.group = group
        if group:
            self.fields['name'].label = f"Nuovo ruolo per {group.name}"
