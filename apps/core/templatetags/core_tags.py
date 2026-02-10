import bleach
import markdown as md
from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe

register = template.Library()

ALLOWED_TAGS = [
    "p", "br", "strong", "em", "ul", "ol", "li", "a",
    "h2", "h3", "h4", "blockquote", "code", "pre",
]
ALLOWED_ATTRIBUTES = {"a": ["href", "title"]}


@register.filter(name="markdown")
def render_markdown(value):
    if not value:
        return ""
    html = md.markdown(value, extensions=["extra"])
    cleaned = bleach.clean(html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)
    return mark_safe(cleaned)


ACTIVE_CLS = "text-primary-700 bg-primary-50/70 font-semibold"
INACTIVE_CLS = "text-gray-600 hover:text-primary-700 hover:bg-gray-50"


@register.simple_tag(takes_context=True)
def active_nav(context, url_name):
    request = context.get("request")
    if request is None:
        return INACTIVE_CLS
    try:
        url_path = reverse(url_name)
    except Exception:
        return INACTIVE_CLS
    is_active = (
        (request.path == "/" and url_path == "/")
        or (url_path != "/" and request.path.startswith(url_path))
    )
    return ACTIVE_CLS if is_active else INACTIVE_CLS
