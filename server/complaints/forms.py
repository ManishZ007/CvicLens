import math

from django import forms

from .models import Complaint


class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ["description", "category", "latitude", "longitude"]

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