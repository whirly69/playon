from django import forms
from .models import Match, MatchPerformance



class MatchForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = ['group', 'date', 'time', 'structure', 'players_per_team', 'is_public']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
        }
        labels = {
            'group': 'Gruppo',
            'date': 'Data',
            'time': 'Ora',
            'structure': 'Struttura',
            'players_per_team': 'Giocatori per squadra',
            'is_public': 'Partita pubblica',
        }

class MatchResultForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = ['score_team1', 'score_team2']
        widgets = {
            'score_team1': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'score_team2': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }
        labels = {
            'score_team1': 'Gol squadra 1',
            'score_team2': 'Gol squadra 2',
        }

class MatchPerformanceForm(forms.ModelForm):
    class Meta:
        model = MatchPerformance
        fields = [ 'goals']
        widgets = {
            
            'goals': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            
        }
        labels = {
            
            'goals': 'Goal',
            
        }