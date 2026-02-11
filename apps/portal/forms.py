from django import forms
from django.db.models import Q

from apps.accounts.models import Profile
from apps.portal.models import ClientProject, Message, ProjectComment
from apps.projects.models import ProjectDocument


class MessageComposeForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["to_user", "subject", "content"]
        widgets = {
            "subject": forms.TextInput(attrs={"class": "w-full", "placeholder": "Objet du message"}),
            "content": forms.Textarea(attrs={"class": "w-full", "rows": 6, "placeholder": "Votre message...", "maxlength": "10000"}),
        }
        labels = {
            "to_user": "Destinataire",
            "subject": "Objet",
            "content": "Message",
        }

    def __init__(self, *args, sender=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.sender = sender
        if sender is None:
            self.fields["to_user"].queryset = self.fields["to_user"].queryset.none()
            return

        from apps.accounts.models import User

        sender_project_ids = ClientProject.objects.filter(
            user=sender
        ).values_list("project_id", flat=True)

        peer_user_ids = ClientProject.objects.filter(
            project_id__in=sender_project_ids
        ).exclude(user=sender).values_list("user_id", flat=True)

        self.fields["to_user"].queryset = User.objects.filter(
            Q(pk__in=peer_user_ids) | Q(is_staff=True)
        ).exclude(pk=sender.pk).distinct()

    def clean_to_user(self):
        to_user = self.cleaned_data["to_user"]
        if self.sender and to_user == self.sender:
            raise forms.ValidationError("Vous ne pouvez pas vous envoyer un message.")
        return to_user


class ProjectCommentForm(forms.ModelForm):
    class Meta:
        model = ProjectComment
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(attrs={
                "class": "w-full rounded-lg border-gray-300",
                "rows": 2,
                "placeholder": "Votre commentaire...",
                "maxlength": "10000",
            }),
        }
        labels = {"content": ""}


class ClientDocumentUploadForm(forms.ModelForm):
    class Meta:
        model = ProjectDocument
        fields = ["title", "file", "category"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "w-full rounded-lg border-gray-300", "placeholder": "Titre"}),
            "category": forms.TextInput(attrs={"class": "w-full rounded-lg border-gray-300", "placeholder": "Catégorie"}),
        }
        labels = {
            "title": "Titre",
            "file": "Fichier",
            "category": "Catégorie",
        }


class ClientProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, label="Prenom", widget=forms.TextInput(attrs={"class": "w-full"}))
    last_name = forms.CharField(max_length=150, label="Nom", widget=forms.TextInput(attrs={"class": "w-full"}))

    class Meta:
        model = Profile
        fields = ["phone", "avatar"]
        widgets = {
            "phone": forms.TextInput(attrs={"class": "w-full", "placeholder": "+227..."}),
        }
        labels = {
            "phone": "Telephone",
            "avatar": "Photo de profil",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields["first_name"].initial = self.instance.user.first_name
            self.fields["last_name"].initial = self.instance.user.last_name

    def save(self, commit=True):
        profile = super().save(commit=commit)
        user = profile.user
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save(update_fields=["first_name", "last_name"])
        return profile
