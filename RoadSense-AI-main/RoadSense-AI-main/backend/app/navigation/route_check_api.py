
from rest_framework.decorators import api_view
from rest_framework.response import Response
from geopy.distance import geodesic
from potholes.models import Pothole

ALERT_DISTANCE_METERS = 100

@api_view(['POST'])
def route_check(request):
    lat = request.data.get("current_lat")
    lng = request.data.get("current_lng")
    if lat is None or lng is None:
        return Response({"error":"Missing GPS"}, status=400)

    user = (float(lat), float(lng))
    nearest, min_d = None, None
    for p in Pothole.objects.filter(status__in=["REPORTED","VERIFIED"]):
        d = geodesic(user, (p.latitude, p.longitude)).meters
        if d <= ALERT_DISTANCE_METERS and (min_d is None or d < min_d):
            nearest, min_d = p, d

    if nearest:
        return Response({
            "alert": True,
            "pothole_id": nearest.id,
            "severity": nearest.severity,
            "distance_meters": round(min_d,1),
            "message": f"Pothole ahead in {int(min_d)} meters. Slow down."
        })
    return Response({"alert": False})
