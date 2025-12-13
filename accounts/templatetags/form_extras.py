from django import template

register = template.Library()

@register.filter(name="add_class")
def add_class(field, css):
    existing = field.field.widget.attrs.get("class", "")
    if existing:
        css = f"{existing} {css}"
    return field.as_widget(attrs={"class": css})
