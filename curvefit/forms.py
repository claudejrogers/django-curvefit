from django import forms

class CurvefitForm(forms.Form):
    MODEL_CHOICES = (
        ('boltzmann', 'Boltzmann sigmoid'),
        ('expdecay', 'Exponential Decay'),
        ('gaussian', 'Gaussian function'),
        ('hill', 'Hill plot'),
        ('ic50', 'Dose Response (ic50)'),
        ('mm', 'Michaelis-Menten'),
        ('modsin', 'Modified sine wave'),
    )
    model = forms.ChoiceField(choices=MODEL_CHOICES, help_text="*")
    m1 = forms.FloatField(label=u"m\u2081", help_text="*",
                        initial=1.0,
                        widget=forms.TextInput(attrs={'size': 10}))
    m2 = forms.FloatField(label=u"m\u2082", help_text="*",
                        initial=1.0,
                        widget=forms.TextInput(attrs={'size': 10}))
    m3 = forms.FloatField(label=u"m\u2083", help_text="*",
                        initial=1.0,
                        widget=forms.TextInput(attrs={'size': 10}))
    m4 = forms.FloatField(label=u"m\u2084", help_text="*",
                        initial=1.0,
                        widget=forms.TextInput(attrs={'size': 10}))
    x_label = forms.CharField(max_length=100, required=False,
                        widget=forms.TextInput(attrs={'size': 50}))
    y_label = forms.CharField(max_length=100, required=False,
                        widget=forms.TextInput(attrs={'size': 50}))
    infile = forms.FileField(label="File", 
                        help_text="* .xls, .txt, and .csv files supported.")
