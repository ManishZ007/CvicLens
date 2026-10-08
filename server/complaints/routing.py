from ai_engine.location import route_complaint

from .models import Department, Ward


def apply_routing(complaint):
    result = route_complaint(
        complaint.category, complaint.latitude, complaint.longitude
    )
    complaint.department = Department.objects.filter(
        code=result.department_code
    ).first()
    complaint.ward = (
        Ward.objects.filter(code=result.ward_code).first()
        if result.ward_code
        else None
    )

    complaint.routing_mode = result.mode
    if not complaint.department or (
        result.ward_code and not complaint.ward
    ):
        complaint.routing_mode = "pending"