from pydantic import BaseModel
from typing import Dict, Optional

class ProductInput(BaseModel):
    name: str
    manufacturer: str
    specs: Dict[str, str]
    description: Optional[str] = None

class ProductOutput(BaseModel):
    seo_title: str
    seo_description: str
    key_specs: Dict[str, str]
    search_queries: list[str]
    commercial_block: str