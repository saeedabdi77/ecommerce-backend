from core.manager.managers import registry


def manager_context(request):
    if not request.path.startswith("/manager/"):
        return {}

    return {
        "manager_menu": registry.get_menu(request),
    }
