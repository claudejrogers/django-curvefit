from django import forms

class CurvefitForm(forms.Form):
    MODEL_CHOICES = (
        ('', '--------'),
        ('boltzmann', 'Boltzmann sigmoid'),
        ('expdecay', 'Exponential Decay'),
        ('gaussian', 'Gaussian function'),
        ('hill', 'Hill plot'),
        ('ic50', 'Dose Response (ic50)'),
        ('mm', 'Michaelis-Menten'),
        ('modsin', 'Modified sine wave'),
    )
    model = forms.CharField(max_length=500, help_text="*",
                            widget=forms.TextInput(attrs={'size': 80}))
    builtin_models = forms.ChoiceField(choices=MODEL_CHOICES, required=False,
                                       label="Built-In Models",
                                       help_text="Optionally select a model from the list")
    m1 = forms.FloatField(label=u"var0", help_text="*",
                        initial=1.0,
                        widget=forms.TextInput(attrs={'size': 10}))
    m2 = forms.FloatField(label=u"var1", help_text="*",
                        initial=1.0,
                        widget=forms.TextInput(attrs={'size': 10}))
    m3 = forms.FloatField(label=u"var2", help_text="*",
                        initial=1.0,
                        widget=forms.TextInput(attrs={'size': 10}))
    m4 = forms.FloatField(label=u"var3", help_text="*",
                        initial=1.0,
                        widget=forms.TextInput(attrs={'size': 10}))
    x_label = forms.CharField(max_length=100, required=False,
                        widget=forms.TextInput(attrs={'size': 50}))
    y_label = forms.CharField(max_length=100, required=False,
                        widget=forms.TextInput(attrs={'size': 50}))
    logscale = forms.BooleanField(label="Plot in Log Scale?",
                                  required=False)
    infile = forms.FileField(label="File", 
                        help_text="* .xls, .txt, and .csv files supported.")
