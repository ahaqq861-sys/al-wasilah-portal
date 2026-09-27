from .models import PortalBranding

def portal_branding_context(request):
    branding = PortalBranding.objects.first()
    if not branding:
        branding = PortalBranding.objects.create()
    return {
        'branding': branding,
        'user_profile': getattr(request.user, 'profile', None) if request.user.is_authenticated else None
    }