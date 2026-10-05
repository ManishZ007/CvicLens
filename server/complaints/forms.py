import math

from django import forms

from .models import Complaint


class ComplaintForm(forms.ModelForm):
    photo = forms.ImageField(required=False)

    class Meta:
        model = Complaint
        fields = ["description", "category", "latitude", "longitude"]

    def clean_photo(self):
        photo = self.cleaned_data.get("photo")
        if not photo:
            return None
        if photo.size > 5 * 1024 * 1024:
            raise forms.ValidationError("Photo must be 5 MB or smaller.")
        if photo.image.format not in {"JPEG", "PNG", "WEBP"}:
            raise forms.ValidationError("Use JPG, PNG, or WebP.")
        return photo

    def clean(self):
        data = super().clean()
        lat = data.get("latitude")
        lng = data.get("longitude")

        if (lat is None) != (lng is None):
            raise forms.ValidationError(
                "Provide both latitude and longitude, or leave both empty."
            )

        for field in ("latitude", "longitude"):
            value = data.get(field)
            if value is not None and not math.isfinite(value):
                self.add_error(field, "Enter a finite coordinate.")

        return data