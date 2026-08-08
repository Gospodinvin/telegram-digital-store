from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from models import Product, Creator, init_db
from config import settings

app = FastAPI(title="Telegram Digital Store API")

# CORS для Mini App
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретный домен
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SessionLocal = init_db(settings.DATABASE_URL)

def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

class ProductResponse(BaseModel):
    id: int
    name: str
    description: str | None
    price_stars: int
    sales_count: int
    creator_id: int

    class Config:
        from_attributes = True

class CreatorResponse(BaseModel):
    telegram_id: int
    username: str | None
    first_name: str | None

    class Config:
        from_attributes = True

@app.get("/api/products")
async def get_products(creator_id: int | None = None):
    db = get_db()
    query = db.query(Product).filter(Product.is_active == True)

    creator = None
    if creator_id:
        query = query.filter(Product.creator_id == creator_id)
        creator = db.query(Creator).filter(Creator.telegram_id == creator_id).first()

    products = query.order_by(Product.sales_count.desc()).all()

    return {
        "products": [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "price_stars": p.price_stars,
                "sales_count": p.sales_count,
                "creator_id": p.creator_id
            } for p in products
        ],
        "creator": {
            "telegram_id": creator.telegram_id,
            "username": creator.username,
            "first_name": creator.first_name
        } if creator else None
    }

@app.get("/api/products/{product_id}")
async def get_product(product_id: int):
    db = get_db()
    product = db.query(Product).filter(Product.id == product_id, Product.is_active == True).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    creator = product.creator

    return {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "price_stars": product.price_stars,
        "sales_count": product.sales_count,
        "creator_id": product.creator_id,
        "creator": {
            "telegram_id": creator.telegram_id,
            "username": creator.username,
            "first_name": creator.first_name
        }
    }

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}