from decouple import config


def get_manager_root_url(request):
    manager_url = config("MANAGER_URL").strip("/")
    parts = request.path.strip("/").split("/")
    index = parts.index(manager_url)
    tenant = parts[index + 1]
    return f"/{manager_url}/{tenant}/"
