from django.utils.deprecation import MiddlewareMixin
from django.utils import translation

class LanguageMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Get language from session or default to English
        language = request.session.get('language', 'en')
        
        # Set the language for this request
        translation.activate(language)
        request.LANGUAGE = language
        
        # Set the Content-Language header for the response
        response = self.get_response(request)
        response['Content-Language'] = language
        return response

    def process_response(self, request, response):
        # Make sure to deactivate the language when done
        translation.deactivate()
        return response 