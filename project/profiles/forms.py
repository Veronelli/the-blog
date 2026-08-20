from django import forms
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import URLValidator

from profiles.models import PublicProfile

_PHOTO_URL_VALIDATOR = URLValidator()


class PublicProfileForm(forms.ModelForm):
    class Meta:
        model = PublicProfile
        fields = (
            "public_username",
            "first_name",
            "last_name",
            "title",
            "subtitle",
            "specialty",
            "short_description",
            "photo_url",
        )

    def clean(self) -> dict:
        cleaned_data = super().clean()
        photo_url = cleaned_data.get("photo_url", "") or ""
        if photo_url:
            try:
                _PHOTO_URL_VALIDATOR(photo_url)
            except DjangoValidationError:
                raise forms.ValidationError({"photo_url": "Enter a valid URL."})
        return cleaned_data