from django.shortcuts import redirect, render
from django.views import View

from apps.contacts.forms import ContactForm


class ContactView(View):
    template_name = "pages/contact.html"

    def get(self, request):
        return render(request, self.template_name, {"form": ContactForm()})

    def post(self, request):
        form = ContactForm(request.POST)
        is_htmx = request.headers.get("HX-Request") == "true"

        if form.is_valid():
            if form.is_honeypot_filled():
                if is_htmx:
                    return render(request, "partials/_contact_success.html")
                return redirect("contact")

            form.save()

            if is_htmx:
                return render(request, "partials/_contact_success.html")
            return redirect("contact")

        if is_htmx:
            return render(request, "partials/_contact_form.html", {"form": form})
        return render(request, self.template_name, {"form": form})
