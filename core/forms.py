from django import forms

class ContattoForm(forms.Form):
    TIPO_SCELTE = [
        ('bug', 'Segnalazione Bug'),
        ('feature', 'Richiesta Funzionalità'),
        ('support', 'Richiesta Supporto'),
        ('feedback', 'Feedback'),
        ('complaint', 'Reclamo'),
        ('privacy', 'Privacy'),
        
        ('altro', 'Altro'),
    ]

    tipo = forms.ChoiceField(choices=TIPO_SCELTE, label="Tipo richiesta")
    messaggio = forms.CharField(widget=forms.Textarea, label="Messaggio")
