
from rest_framework.decorators import api_view
from rest_framework.response import Response
from potholes.models import Pothole
from django.utils.timezone import now

@api_view(['POST'])
def feedback(request):
    pid = request.data.get("pothole_id")
    fb = request.data.get("feedback") # exists | fixed
    if not pid or not fb:
        return Response({"error":"Bad request"}, status=400)
    p = Pothole.objects.get(id=pid)
    if fb == "exists":
        p.confidence_score = min(p.confidence_score+0.1,1.0)
        p.last_confirmed = now()
    elif fb == "fixed":
        p.confidence_score -= 0.2
        if p.confidence_score <= 0.3:
            p.status = "FIXED"
    p.save()
    return Response({"ok": True})
