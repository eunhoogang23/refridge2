from typing import List, Optional
from pydantic import BaseModel


# --- /scan/package ---
class PackageScanResult(BaseModel):
    name: str
    category: str
    expiryDateOnPackage: Optional[str] = None
    estimatedShelfLifeDays: int


# --- /scan/receipt ---
class ReceiptItem(BaseModel):
    name: str
    category: str
    estimatedShelfLifeDays: int


class ReceiptScanResult(BaseModel):
    purchaseDate: Optional[str] = None
    items: List[ReceiptItem]


# --- /recipe/recommend ---
class Recipe(BaseModel):
    title: str
    usesUrgent: List[str]
    ingredients: List[str]
    steps: List[str]


class RecipeRecommendation(BaseModel):
    recipes: List[Recipe]
