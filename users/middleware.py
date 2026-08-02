from django.shortcuts import redirect
from .models import Colony


WELCOME_EXEMPT = [
    '/welcome/',
    '/login/',
    '/logout/',
    '/registro/',
    '/settings/',
    '/admin/',
    '/static/',
    '/api/',
]


class ColonyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            user_colony = request.user.owned_colonies.filter(is_guest=False).first()
            if user_colony:
                request.colony = user_colony
                request.session['colony_id'] = user_colony.id
            else:
                request.colony = self._resolve_colony(request, is_authenticated=True)
        else:
            request.colony = self._resolve_colony(request, is_authenticated=False)

        request.session.modified = True

        path = request.path
        if not any(path.startswith(p) for p in WELCOME_EXEMPT):
            if not request.user.is_authenticated and not request.session.get('welcome_seen'):
                return redirect('users:welcome')

        response = self.get_response(request)
        return response

    def _resolve_colony(self, request, is_authenticated):
        colony_id = request.session.get('colony_id')
        if colony_id:
            try:
                return Colony.objects.get(id=colony_id)
            except Colony.DoesNotExist:
                pass
        return self._create_colony(request, is_authenticated)

    def _create_colony(self, request, is_authenticated):
        from finances.models import Currency

        if is_authenticated:
            name = f'Colonia de {request.user.username}'
            colony = Colony.objects.create(name=name, is_guest=False, owner=request.user)
        else:
            colony = Colony.objects.create(name='Colonia invitada', is_guest=True)

        default_currency = Currency.objects.filter(colony__isnull=True).first()
        if default_currency:
            colony.default_currency = default_currency
            colony.save(update_fields=['default_currency'])

        request.session['colony_id'] = colony.id
        request.session['welcome_seen'] = True
        return colony
