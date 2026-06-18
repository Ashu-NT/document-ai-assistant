from dataclasses import dataclass


@dataclass(frozen=True)
class TrackingOptions:
    activity: bool = True
    audit: bool = False
    event: bool = False