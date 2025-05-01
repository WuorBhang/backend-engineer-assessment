from django import forms
from .models import Bid

class BidAdminForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        amount = cleaned_data.get('amount')
        auction = cleaned_data.get('auction')

        if auction and amount and amount <= auction.current_price:
            raise forms.ValidationError("Bid must be higher than the current auction price.")

        return cleaned_data
