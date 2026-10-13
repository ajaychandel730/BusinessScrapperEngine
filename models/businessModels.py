

from dataclasses import dataclass, field


@dataclass
class GoogleMapBusinessInfo:
    name: str = None
    address: str = None
    website: str = None
    phone_number: str = None
    rating: int = None
    
@dataclass 
class CompanyWebsiteInfo:
    emails:list[str]=field(default_factory=list)
    
    
@dataclass
class CombinedCompanyDetails(GoogleMapBusinessInfo, CompanyWebsiteInfo):
    pass    