from django import forms

from apps.contacts.models import Contact


class ContactForm(forms.ModelForm):
    company_fax = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = Contact
        fields = ["name", "email", "phone", "subject", "message"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Votre nom complet", "maxlength": 255}),
            "email": forms.EmailInput(attrs={"placeholder": "votre@email.com"}),
            "phone": forms.TextInput(attrs={"placeholder": "+227 xx xx xx xx"}),
            "subject": forms.TextInput(attrs={"placeholder": "Objet de votre message", "maxlength": 255}),
            "message": forms.Textarea(attrs={"placeholder": "Votre message...", "rows": 5}),
        }
        labels = {
            "name": "Nom",
            "email": "Email",
            "phone": "Téléphone",
            "subject": "Sujet",
            "message": "Message",
        }

    def is_honeypot_filled(self):
        return bool(self.cleaned_data.get("company_fax"))
