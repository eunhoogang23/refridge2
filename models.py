from sqlalchemy import Column, Integer, String, Date
from database import Base

class FridgeItem(Base):
    __tablename__ = "fridge_items"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    category = Column(String)
    purchase_date = Column(Date)
    shelf_life_days = Column(Integer)
    expiry_date = Column(Date)