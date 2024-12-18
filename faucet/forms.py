from django import forms


# POST data sent when a client requests funds from the faucet
class FaucetRequestForm(forms.Form):
    address = forms.CharField(max_length=42, min_length=42)
