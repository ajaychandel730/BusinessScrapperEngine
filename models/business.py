

from dataclasses import dataclass


@dataclass
class Business:
    name: str = None
    address: str = None
    website: str = None
    phone_number: str = None