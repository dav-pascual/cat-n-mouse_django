from django import forms
from django.contrib.auth.models import User
from datamodel.models import Move, GameStatus, PlayerTypes
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import MaxValueValidator, MinValueValidator


class SignupForm(forms.ModelForm):
    """
    @author: David Pascual
    """
    password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(label=("Repeat Password"),
                                widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("username",)

    def clean_password2(self):
        password = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password2")
        if password and password2 and password != password2:
            error = "Password and Repeat password are not the same"
            self.add_error('password2', forms.ValidationError(error))
        return password2

    def clean_password(self):
        password = self.cleaned_data.get("password")
        try:
            validate_password(password, self.instance)
        except forms.ValidationError as e:
            self.add_error('password', e)
        return password

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class MoveForm(forms.ModelForm):
    """
    @author: David Pascual
    """
    origin = forms.IntegerField(validators=[MinValueValidator(0),
                                            MaxValueValidator(63)],
                                widget=forms.HiddenInput())
    target = forms.IntegerField(validators=[MinValueValidator(0),
                                            MaxValueValidator(63)],
                                widget=forms.HiddenInput())

    class Meta:
        model = Move
        fields = ('origin', 'target')


class FilterSelectForm(forms.Form):
    """
    @author: David Pascual
    """
    CHOICES_PLAYER = (('all', 'All'), (PlayerTypes.CAT, 'Cat'),
                      (PlayerTypes.MOUSE, 'Mouse'),)
    select_player = forms.ChoiceField(choices=CHOICES_PLAYER,
                                      label='Filter by player type:')

    CHOICES_STATUS = (('all', 'All'), (GameStatus.CREATED, 'Created'),
                      (GameStatus.ACTIVE, 'Active'),
                      (GameStatus.FINISHED, 'Finished'),)
    select_status = forms.ChoiceField(
        choices=CHOICES_STATUS, label='Filter by status:')
