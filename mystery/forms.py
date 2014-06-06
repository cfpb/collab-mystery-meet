from django import forms
from mystery.models import Interest
from core.models import OfficeLocation, OrgGroup
from django.forms.util import ErrorList


class LocationModelMultipleChoiceField(forms.ModelMultipleChoiceField):

    def label_from_instance(self, obj):
        return obj.name


class InterestForm(forms.ModelForm):

    class Meta:
        model = Interest
        exclude = ('owner', 'is_active', 'match', 'created', 'updated',
                   'for_lunch', 'for_coffee', 'video_chat')

    def __init__(self, *args, **kwargs):
        super(InterestForm, self).__init__(*args, **kwargs)
        self.fields['locations'] = LocationModelMultipleChoiceField(
            widget=forms.CheckboxSelectMultiple,
            queryset=OfficeLocation.objects.exclude(id="Remote"),
            required=False)
        self.fields['departments'] = forms.ModelMultipleChoiceField(
            widget=forms.CheckboxSelectMultiple,
            queryset=OrgGroup.objects.filter(parent__isnull=True))
        choices = ((Interest.CHOICE_LUNCH, 'Lunch'),
                   (Interest.CHOICE_COFFEE, 'Coffee'),
                   (Interest.CHOICE_VIDEO, 'Video Chat'))
        self.fields['meet_choice'] = forms.TypedChoiceField(
            choices=choices,
            widget=forms.RadioSelect)
        self.fields['departments'].initial = self.fields[
            'departments'].queryset.all()

    def is_valid(self):
        is_valid = super(InterestForm, self).is_valid()

        if is_valid and len(self.cleaned_data['locations']) == 0 and \
           self.cleaned_data['meet_choice'] != Interest.CHOICE_VIDEO:
            self._errors['locations'] = ErrorList(
                [u"This field is required unless Video Chat is selected"])
            is_valid = False

        return is_valid

    def save(self, commit=True):
        instance = super(InterestForm, self).save(commit=False)
        meet_choice = self.cleaned_data['meet_choice']
        if meet_choice == Interest.CHOICE_LUNCH:
            instance.for_lunch = True
        elif meet_choice == Interest.CHOICE_COFFEE:
            instance.for_coffee = True
        else:  # CHOICE_VIDEO
            instance.video_chat = True
        if commit:
            instance.initial_save(locations=self.cleaned_data['locations'],
                                  departments=self.cleaned_data['departments'])
        return instance
