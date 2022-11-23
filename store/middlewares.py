from django.contrib import messages
from django.core.cache import cache
from django.utils.deprecation import MiddlewareMixin


class CheckUserVisit(MiddlewareMixin):

    def process_request(self, request):
        request_url = request.path.replace("/", "")
        if request.user.is_authenticated and not request.user.is_superuser and \
                request_url in ['returns', 'purchases']:
            counter_session = request.session.get('counter_session', 0)
            counter_session += 1
            if counter_session == 4:
                messages.info(request, f'This is your 4th visit')
                request.session['counter_session'] = 0
            else:
                request.session['counter_session'] = counter_session
            counter_cache = cache.get('counter_cache', 0)
            counter_cache += 1
            if counter_cache == 10:
                messages.info(request, 'You are our 10th customer')
                cache.set('counter_cache', 0)
            else:
                cache.set('counter_cache', counter_cache)
