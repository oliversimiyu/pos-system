from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .services import process_mpesa_callback


@csrf_exempt
@require_http_methods(["POST"])
def mpesa_callback(request):
    """Handle M-Pesa callback/webhook"""
    try:
        callback_data = json.loads(request.body)
        result = process_mpesa_callback(callback_data)
        
        if result.get('success'):
            return JsonResponse({
                'ResultCode': 0,
                'ResultDesc': 'Accepted'
            })
        else:
            return JsonResponse({
                'ResultCode': 1,
                'ResultDesc': result.get('error', 'Processing failed')
            })
    
    except Exception as e:
        return JsonResponse({
            'ResultCode': 1,
            'ResultDesc': str(e)
        })
