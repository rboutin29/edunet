'''
Contains the forms for the EduNet website.
'''
from django import forms

error_messages = {'ValueError': 'Value must be less then ten.'}

class TKForm(forms.Form):
    '''Class used to display the form that gets tree transcripts.'''
    np = forms.IntegerField(label='Nouns per Paragraph', max_value=10)
    nl = forms.IntegerField(label='Nouns per Lecture', max_value=10)
    t = forms.IntegerField(label='Transcript')
