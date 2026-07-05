from installation.enums import InstallationRequestStatus
from installation.models import InstallationRequest


def resolve_draft_installation_request(user=None, guest_uid=None):
    if user.is_authenticated:
        request = user.installation_requests.filter(status=InstallationRequestStatus.DRAFT).first()
        if request:
            return request

    if guest_uid:
        request = InstallationRequest.objects.filter(status=InstallationRequestStatus.DRAFT, guest_uid=guest_uid,
                                                     user__isnull=True).first()
        if request:
            if user.is_authenticated:
                request.user = user
                request.save(update_fields=['user'])
            return request
    return None


def get_or_create_draft_installation_request(user=None, guest_uid=None):
    draft_installation_request = resolve_draft_installation_request(user, guest_uid)
    if draft_installation_request:
        return draft_installation_request

    if user and user.is_authenticated:
        return InstallationRequest.objects.create(user=user)
    elif guest_uid:
        return InstallationRequest.objects.create(guest_uid=guest_uid)

    return None
