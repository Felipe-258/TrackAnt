from django.shortcuts import redirect
from .models import Colony


WELCOME_EXEMPT = [
    '/welcome/',
    '/login/',
    '/logout/',
    '/registro/',
    '/admin/',
    '/static/',
    '/api/',
]


class ColonyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        colony_id = request.session.get('colony_id')
        if colony_id:
            try:
                request.colony = Colony.objects.get(id=colony_id)
            except Colony.DoesNotExist:
                request.colony = self._create_guest(request)
        else:
            request.colony = self._create_guest(request)

        path = request.path
        if not any(path.startswith(p) for p in WELCOME_EXEMPT):
            if not request.session.get('welcome_seen'):
                return redirect('users:welcome')

        response = self.get_response(request)
        return response

    def _create_guest(self, request):
        colony = Colony.objects.create(
            name='Colonia invitada',
            is_guest=True,
        )
        request.session['colony_id'] = colony.id
        return colony
