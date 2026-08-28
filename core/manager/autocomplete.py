from django.apps import apps
from django.db.models import Q


AUTOCOMPLETE_MODELS = {
    "product.producttype": {
        "search_fields": ("name", "slug", "category__name", "brand__name"),
        "select_related": ("category", "brand"),
        "label": lambda obj: f"{obj.name} — {obj.category}" if getattr(obj, "category_id", None) else str(obj),
    },
    "product.product": {
        "search_fields": ("serial", "product_type__name", "product_type__slug"),
        "select_related": ("product_type", "product_type__category"),
        "label": lambda obj: f"{obj.serial} ({obj.product_type})",
    },
    "product.category": {
        "search_fields": ("name", "slug"),
        "label": str,
    },
    "product.attributevalue": {
        "search_fields": ("value", "slug", "attribute__name"),
        "select_related": ("attribute",),
        "label": lambda obj: f"{obj.attribute}: {obj.value}",
    },
    "user.user": {
        "search_fields": ("phone_number", "first_name", "last_name", "email"),
        "label": lambda obj: f"{obj.phone_number} — {obj.get_full_name() or obj.phone_number}".strip(" —"),
    },
    "order.order": {
        "search_fields": ("tracking_code", "user__phone_number"),
        "select_related": ("user",),
        "label": lambda obj: f"#{obj.tracking_code}",
    },
    "order.orderitem": {
        "search_fields": ("order__tracking_code", "product_type__name"),
        "select_related": ("order", "product_type"),
        "label": lambda obj: f"#{obj.order.tracking_code} — {obj.product_type}",
    },
    "installation.game": {
        "search_fields": ("name",),
        "label": str,
    },
    "installation.installationrequest": {
        "search_fields": ("tracking_code", "user__phone_number"),
        "select_related": ("user",),
        "label": lambda obj: f"#{obj.tracking_code}",
    },
    "repair.repairdevicetype": {
        "search_fields": ("name",),
        "label": str,
    },
    "repair.repairproblemtype": {
        "search_fields": ("name",),
        "label": str,
    },
}


def get_model_key(model):
    return f"{model._meta.app_label}.{model._meta.model_name}"


def get_autocomplete_config(model):
    config = AUTOCOMPLETE_MODELS.get(get_model_key(model), {})
    return {
        "search_fields": config.get("search_fields", ("name",)),
        "select_related": config.get("select_related", ()),
        "prefetch_related": config.get("prefetch_related", ()),
        "label": config.get("label", str),
    }


def uses_autocomplete(model):
    return get_model_key(model) in AUTOCOMPLETE_MODELS


def get_model(app_label, model_name):
    return apps.get_model(app_label, model_name)


def search_models(app_label, model_name, query="", *, pk=None, limit=20):
    model = get_model(app_label, model_name)
    config = get_autocomplete_config(model)
    queryset = model._default_manager.all()

    if config["select_related"]:
        queryset = queryset.select_related(*config["select_related"])

    if config["prefetch_related"]:
        queryset = queryset.prefetch_related(*config["prefetch_related"])

    if pk:
        queryset = queryset.filter(pk=pk)
    elif query:
        terms = [term for term in query.split() if term]

        for term in terms:
            term_query = Q()
            for field in config["search_fields"]:
                term_query |= Q(**{f"{field}__icontains": term})
            queryset = queryset.filter(term_query)

    if not pk:
        if not queryset.query.order_by:
            queryset = queryset.order_by("pk")
        queryset = queryset[:limit]

    label_fn = config["label"]
    return [{"id": obj.pk, "label": label_fn(obj)} for obj in queryset]
