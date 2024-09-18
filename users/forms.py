from django import forms

from users.models import User
from django.contrib.auth.hashers import make_password


class UserRegistrationForm(forms.ModelForm):
    user_type = forms.ChoiceField(
        choices=((User.BUYER, "Buyer"), (User.FARMER, "Farmer"))
    )

    class Meta:
        model = User
        fields = (
            "email",
            "phone",
            "full_name",
            "password",
            "user_type",
            "date_of_birth",
        )

    def save(self, commit=True):
        # Create an instance of the model with the form data
        instance = super().save(commit=False)

        # Perform additional logic here, e.g., hashing a password
        # if you are using a password field
        if self.cleaned_data.get("password"):
            instance.password = make_password(self.cleaned_data["password"])

        # Save the instance to the database if commit is True
        if commit:
            instance.save()

        return instance
