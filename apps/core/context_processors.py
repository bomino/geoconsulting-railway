from datetime import datetime


def company_info(request):
    return {
        "company_name": "GéoConsulting SARLU",
        "company_slogan": "La qualité au service du développement durable",
        "company_address": "Tchangarey, Niamey, Niger",
        "company_phone1": "+227 90 53 53 23",
        "company_phone2": "+227 82 24 24 20",
        "company_email": "info@mygeoconsulting.com",
        "company_email2": "support@mygeoconsulting.com",
        "company_hours": "Lundi au vendredi, 8h20 — 17h00",
        "company_whatsapp": "https://wa.me/22790535323",
        "company_map_lat": "13.521389",
        "company_map_lng": "2.105278",
        "current_year": datetime.now().year,
    }
