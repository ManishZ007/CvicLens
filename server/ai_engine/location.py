"""Validated location routing for a clearly labelled, synthetic college demo.

The rectangles below are NOT official Pune ward boundaries. No geocoding or
PostGIS is claimed. Replace the resolver with verified boundaries before rollout.
"""

from dataclasses import asdict, dataclass

from .contracts import Category, Coordinates


DEPARTMENTS = {
    "roads": "Roads", "sanitation": "Sanitation", "water": "Water",
    "electrical": "Electrical", "drainage": "Drainage", "general": "General review",
}
CATEGORY_DEPARTMENT = {
    Category.POTHOLE: "roads", Category.GARBAGE: "sanitation",
    Category.WATER: "water", Category.LIGHT: "electrical",
    Category.DRAIN: "drainage", Category.OTHER: "general",
}


@dataclass(frozen=True)
class DemoWard:
    code: str
    name: str
    south: float
    north: float
    west: float
    east: float

    def contains(self, point: Coordinates) -> bool:
        # Half-open boundaries avoid assigning a shared edge to two wards.
        return (self.south <= point.latitude < self.north
                and self.west <= point.longitude < self.east)


DEMO_WARDS = (
    DemoWard("DEMO-A", "Demo zone A (not an official ward)", 18.50, 18.55, 73.80, 73.85),
    DemoWard("DEMO-B", "Demo zone B (not an official ward)", 18.50, 18.55, 73.85, 73.90),
)


@dataclass(frozen=True)
class RoutingResult:
    department_code: str
    department_name: str
    ward_code: str | None
    ward_name: str | None
    mode: str
    reason: str

    def to_dict(self):
        return asdict(self)


def route_complaint(category, latitude=None, longitude=None) -> RoutingResult:
    department = CATEGORY_DEPARTMENT[Category(category)]
    if latitude is None and longitude is None:
        return RoutingResult(department, DEPARTMENTS[department], None, None,
                             "pending", "Location required for ward routing.")
    if latitude is None or longitude is None:
        raise ValueError("Both latitude and longitude are required together.")
    point = Coordinates(latitude, longitude)
    matches = [ward for ward in DEMO_WARDS if ward.contains(point)]
    if len(matches) == 1:
        ward = matches[0]
        return RoutingResult(department, DEPARTMENTS[department], ward.code, ward.name,
                             "demo", "Synthetic demo zone only; not an official municipal ward.")
    return RoutingResult(department, DEPARTMENTS[department], None, None,
                         "outside_demo", "Outside configured demo zones; manual routing required.")
