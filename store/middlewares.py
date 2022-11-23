from datetime import datetime

from django.contrib import messages
from django.contrib.auth import logout
from django.core.cache import cache
from django.http import HttpResponseRedirect
from django.utils.deprecation import MiddlewareMixin

from config.settings import INACTIVITY_TIME_LIMIT


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


class AutoLogout(MiddlewareMixin):

    def process_request(self, request):
        if request.user.is_authenticated and not request.user.is_superuser:
            now = datetime.now()
            last_activity_time = request.session.get('last_activity_time', now.isoformat())
            inactivity_period = now - datetime.fromisoformat(last_activity_time)
            if inactivity_period.seconds > INACTIVITY_TIME_LIMIT:
                logout(request)
                return HttpResponseRedirect('/login')
            request.session['last_activity_time'] = now.isoformat()
