from dataclasses import asdict, dataclass, field
from datetime import datetime
import json
import os

from models.businessModels import CombinedCompanyDetails, GoogleMapBusinessInfo


@dataclass
class BusinessManager:
    business_list: list[CombinedCompanyDetails] = field(default_factory=list)

    def dataframe(self):
        return pd.json_normalize(
            (asdict(business) for business in self.business_list), sep=""
        )

    def save_to_excel(self, filename):
        self.dataframe().to_excel(
            f"{filename}-{datetime.now().strftime("%d-%m-%Y_%H-%M-%S")}.xlsx",
            index=False,
        )

    def save_to_json(self, filename):
        target_dir = "data"

        os.makedirs(target_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
        file_path = os.path.join(target_dir, f"{filename}-{timestamp}.json")

        data = [asdict(business) for business in self.business_list]

        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

    def add_company(
        self,
        name: str | None,
        address: str | None,
        website: str | None,
        phone_number: str | None,
        rating:str|None,
        emails:list[str]
    ):
        business = CombinedCompanyDetails()
        business.name = name
        business.address = address
        business.website = website
        business.phone_number = phone_number
        business.rating=rating
        business.emails = emails
        self.business_list.append(business)
