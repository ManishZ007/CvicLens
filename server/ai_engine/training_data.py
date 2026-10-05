"""Small hand-authored English development dataset, not municipal ground truth."""

TRAINING = {
    "pothole": [
        "deep pothole on road", "potholes damaging vehicles on street",
        "road surface broken with holes", "crater in asphalt needs repair",
        "uneven damaged road pavement", "large hole causing road accidents",
    ],
    "garbage": [
        "garbage pile not collected", "trash bins overflowing with waste",
        "rubbish dumped outside market", "waste collection truck missing",
        "litter and refuse on footpath", "rotting garbage needs collection",
    ],
    "water": [
        "water pipe leaking", "burst water pipeline flooding street",
        "no drinking water supply", "broken water main needs repair",
        "tap leaking clean water", "low pressure in water supply",
    ],
    "light": [
        "streetlight not working", "street lights dark at night",
        "broken lamp on pole", "streetlight bulb flickering",
        "public lighting stopped working", "street lamp needs replacement",
    ],
    "drain": [
        "blocked drain overflowing", "sewage spilling from sewer",
        "drainage clogged after rain", "open manhole on footpath",
        "sewer blockage causing dirty water overflow", "drain cover missing",
    ],
    "other": [
        "fallen tree blocking entrance", "loud noise from construction",
        "stray dogs chasing people", "park bench broken",
        "illegal parking outside gate", "public wall damaged",
    ],
}

# Never used for training. Small illustrative evaluation, not production accuracy.
EVALUATION = [
    ("pothole", "Potholes near the school need repair"),
    ("pothole", "Asphalt crater damaging vehicles"),
    ("garbage", "Rubbish and litter near the shops"),
    ("garbage", "Overflowing trash bins outside school"),
    ("water", "Drinking water supply stopped"),
    ("water", "Leaking pipeline outside school"),
    ("light", "Streetlight flickering near school"),
    ("light", "Public lighting dark at night"),
    ("drain", "Sewage overflow near the shops"),
    ("drain", "Missing manhole cover near school"),
    ("other", "Stray dogs near the shops"),
    ("other", "Loud construction noise at night"),
]
