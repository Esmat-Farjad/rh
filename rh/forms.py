from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm, SetPasswordForm, PasswordChangeForm
from django.contrib.auth import get_user_model, password_validation


User = get_user_model()

class RegisterForm(UserCreationForm):
    """Subclass User Registration form"""

    # TODO: Add the custom user details in future
    class Meta:
        model = User
        fields = ['name', 'username', 'email', 'password1', 'password2', 'organization']

    def clean_username(self):
        """check if username already exists"""
        username = self.cleaned_data.get("username")
        qs = User.objects.filter(username__iexact=username)
        if qs.exists():
            raise forms.ValidationError(
                f"{username} is an invalid username, please pick another."
            )
        return username

    def clean_email(self):
        """check if email already exists"""
        email = self.cleaned_data.get("email")
        qs = User.objects.filter(email__iexact=email)
        if qs.exists():
            raise forms.ValidationError(
                f"{email} is an invalid email address, please pick another."
            )
        return email


class UserPasswordChangeForm(PasswordChangeForm):
    """Subclass Password change form to remove labels and classes"""

    def __init__(self, *args, **kwargs):
        """Call super"""
        super(UserPasswordChangeForm, self).__init__(*args, **kwargs)
    
    old_password = forms.CharField(
        label='',
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "current-password", 
                "autofocus": True,
                'class': 'form-control',
                'placeholder': 'Old Password',
                'type': 'password',
                'name': 'old_password',
                
            }
        ),
    )

    new_password1 = forms.CharField(label='', 
        help_text=password_validation.password_validators_help_text_html(),
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'New Password',
                'type': 'password',
                'name': 'new_password1',
                'autocomplete': 'new-password'
            }
        ),
    )
    new_password2 = forms.CharField(label='', 
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Confirm New Password',
                'type': 'password',
                'name': 'new_password2',
                "autocomplete": "new-password"
            }
        ),
    )

class UserSetPasswordForm(SetPasswordForm):
    """Override password reset form to add styling to the input fields"""

    def __init__(self, *args, **kwargs):
        """Call super"""
        super(UserSetPasswordForm, self).__init__(*args, **kwargs)

    new_password1 = forms.CharField(label='', 
        help_text=password_validation.password_validators_help_text_html(),
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'New Password',
                'type': 'password',
                'name': 'new_password1',
                'autocomplete': 'new-password'
            }
        ),
    )
    new_password2 = forms.CharField(label='', 
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Confirm New Password',
                'type': 'password',
                'name': 'new_password2',
                "autocomplete": "new-password"
            }
        ),
    )


class UserPasswordResetForm(PasswordResetForm):
    """Override password reset form to add styling to the input fields"""

    def __init__(self, *args, **kwargs):
        """Call super"""
        super(UserPasswordResetForm, self).__init__(*args, **kwargs)

    email = forms.EmailField(label='', 
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'e.g abc@gmail.com',
                'type': 'email',
                'name': 'email'
            }
        ),
    )


class ProjectForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={
        "class":"w-full rounded-lg focus:ring-primary-600 focus:border-primary-600"
    }), label='Project Title', max_length=100)
    
    description = forms.CharField(widget=forms.Textarea(attrs={
        "class":"w-full rounded-lg focus:ring-primary-600 focus:border-primary-600"
    }), label='Description')
    start_date = forms.DateField(widget=forms.widgets.TextInput(attrs={
        "type":"date",
        "class": "focus:ring-primary-600 rounded-lg focus:border-primary-600 w-full"
    }), label='Start date')
    end_date = forms.DateField(widget=forms.widgets.TextInput(attrs={
        "type":"date",
        "class": " focus:ring-primary-600 rounded-lg focus:border-primary-600 w-full"
    }), label='End date')
