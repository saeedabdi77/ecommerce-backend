from decouple import config


def get_manager_root_url(self):
    parts = self.request.path.strip("/").split("/")
    return "/" + "/".join(parts[:2])

def get_manager_url(request, slug=None):
    parts = request.path.strip("/").split("/")

    if len(parts) < 2:
        return "/"

    root = "/" + "/".join(parts[:2]) + "/"

    if slug:
        return f"{root}{slug}/"

    return root
