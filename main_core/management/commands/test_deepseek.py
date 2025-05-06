from django.core.management.base import BaseCommand
from utils.deepseek_api import deepseek_api
import json
import logging

class Command(BaseCommand):
    help = 'Test DeepSeek API connection'

    def handle(self, *args, **kwargs):
        # Set up logging
        logging.basicConfig(
            filename='deepseek_test.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        try:
            logging.info('Testing DeepSeek API connection...')
            self.stdout.write('Testing DeepSeek API connection...')
            
            response = deepseek_api.generate_response('你好')
            
            logging.info(f'Response received: {response}')
            self.stdout.write(self.style.SUCCESS(f'\nResponse received:\n{response}'))
            
        except Exception as e:
            error_msg = f'Error: {str(e)}'
            logging.error(error_msg)
            self.stdout.write(self.style.ERROR(f'\n{error_msg}'))