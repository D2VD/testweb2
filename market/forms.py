from django import forms

from .models import Region, Subregion

PAYMENT_OPTIONS = (
    ("C", "Cash"),
    ("P", "PayPal"),
)


class CheckoutForm(forms.Form):
    address = forms.CharField(
        max_length=200,
        required=True,
        label="Address",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "123, Quang Trung St, Ward 10",
            }
        ),
    )
    address2 = forms.CharField(
        max_length=200,
        required=False,
        label="Address 2 (Optional)",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Apartment, block, suite, etc.",
            }
        ),
    )
    region = forms.ModelChoiceField(
        queryset=Region.objects.all(),
        label="Province/City",
        empty_label="Select",
        widget=forms.Select({"class": "form-control"}),
    )
    subregion = forms.ModelChoiceField(
        queryset=Subregion.objects.none(),
        label="District/City",
        empty_label="Select",
        widget=forms.Select({"class": "form-control"}),
    )
    # same_shipping_address = forms.BooleanField(required=False)
    # save_info = forms.BooleanField(required=False)
    # payment_option = forms.ChoiceField(choices=PAYMENT_OPTIONS)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "region" in self.data:  # Check if region data is submitted
            try:
                region_id = int(self.data.get("region"))
                self.fields["subregion"].queryset = Subregion.objects.filter(
                    region_id=region_id
                )
            except (ValueError, TypeError):
                pass
