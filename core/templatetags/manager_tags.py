from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def query_string(context, **kwargs):
    request = context["request"]
    params = request.GET.copy()

    for key, value in kwargs.items():
        if value is None:
            params.pop(key, None)
        elif value == "":
            params.pop(key, None)
        else:
            params[key] = value

    params.pop("page", None)
    encoded = params.urlencode()
    return f"?{encoded}" if encoded else "?"


@register.simple_tag(takes_context=True)
def page_url(context, page_number):
    request = context["request"]
    params = request.GET.copy()
    params["page"] = page_number
    encoded = params.urlencode()
    return f"?{encoded}" if encoded else "?"


@register.simple_tag(takes_context=True)
def remove_filter(context, filter_name):
    request = context["request"]
    params = request.GET.copy()
    params.pop(filter_name, None)
    params.pop("page", None)
    encoded = params.urlencode()
    return f"?{encoded}" if encoded else "."


@register.simple_tag(takes_context=True)
def sort_url(context, ordering_name):
    request = context["request"]
    current = request.GET.get("ordering", "")

    if current == ordering_name:
        new_ordering = f"-{ordering_name}"
    elif current == f"-{ordering_name}":
        new_ordering = ordering_name
    else:
        new_ordering = ordering_name

    params = request.GET.copy()
    params["ordering"] = new_ordering
    params.pop("page", None)
    encoded = params.urlencode()
    return f"?{encoded}" if encoded else "?"


@register.simple_tag(takes_context=True)
def hidden_get_params(context, *exclude):
    request = context["request"]
    excluded = set(exclude)
    params = []

    for key, values in request.GET.lists():
        if key in excluded:
            continue

        for value in values:
            params.append((key, value))

    return params


@register.filter
def manager_icon(icon_name):
    icons = {
        "folder": "📁",
        "tag": "🏷",
        "box": "📦",
        "image": "🖼",
        "star": "⭐",
        "users": "👥",
        "list": "📋",
        "settings": "⚙",
        "collection": "📚",
    }
    return icons.get(icon_name, "•")
