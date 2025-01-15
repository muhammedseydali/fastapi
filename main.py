# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel


# from enum import Enum

# app = FastAPI()


# class Item(BaseModel):
#     text: str = None
#     is_done: bool = False


# items = []


# @app.get("/")
# def root():
#     return {"Hello": "World"}

# @app.get("/hello")
# async def hello():
#     return "Welcome"


# @app.get("/hello/{name}")
# async def hello(name):
#     return f"Welcome {name}"

# class AvailableCuisines(str, Enum):
#     indian = "indian"
#     american = "american"
#     italian = "italian"
    
# food_items = {
#     'indian' : [ "Samosa", "Dosa" ],
#     'american' : [ "Hot Dog", "Apple Pie"],
#     'italian' : [ "Ravioli", "Pizza"]
# }

# @app.get("/get_items/{cuisine}")
# async def get_items(cuisine: AvailableCuisines):
#     return food_items.get(cuisine)


# coupon_code = {
#     1: '10%',
#     2: '20%',
#     3: '30%'
# }

# @app.get("/get_coupon/{code}")
# async def get_items(code: int):
#     return { 'discount_amount': coupon_code.get(code) }


# @app.post("/items")
# def create_item(item: Item):
#     items.append(item)
#     return items


# @app.get("/items", response_model=list[Item])
# def list_items(limit: int = 10):
#     return items[0:limit]


# @app.get("/items/{item_id}", response_model=Item)
# def get_item(item_id: int) -> Item:
#     if item_id < len(items):
#         return items[item_id]
#     else:
#         raise HTTPException(status_code=404, detail=f"Item {item_id} not found")

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from schemas import GenreURLChoices, Band
from enum import Enum

app = FastAPI()




# Model for items
class Item(BaseModel):
    text: str
    is_done: bool = False


# In-memory database for items
items = []


@app.get("/")
def root():
    return {"message": "Welcome to the FastAPI CRUD API"}


@app.get("/hello")
async def hello():
    return "Welcome"


@app.get("/hello/{name}")
async def hello(name: str):
    return f"Welcome {name}"


# Enum for cuisine types
class AvailableCuisines(str, Enum):
    indian = "indian"
    american = "american"
    italian = "italian"
    
food_items = {
    'indian': ["Samosa", "Dosa"],
    'american': ["Hot Dog", "Apple Pie"],
    'italian': ["Ravioli", "Pizza"]
}

@app.get("/get_items/{cuisine}")
async def get_items(cuisine: AvailableCuisines):
    return {"items": food_items.get(cuisine)}


coupon_code = {
    1: '10%',
    2: '20%',
    3: '30%'
}

@app.get("/get_coupon/{code}")
async def get_coupon(code: int):
    discount = coupon_code.get(code)
    if not discount:
        raise HTTPException(status_code=404, detail="Coupon code not found")
    return {"discount_amount": discount}


# CRUD Endpoints

# Create an item
@app.post("/items", response_model=Item)
def create_item(item: Item):
    items.append(item)
    return item


# Read all items
@app.get("/items", response_model=list[Item])
def list_items(limit: int = 10):
    return items[:limit]


# Read a specific item
@app.get("/items/{item_id}", response_model=Item)
def get_item(item_id: int):
    if item_id < len(items):
        return items[item_id]
    else:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")


# Update an item 
@app.put("/items/{item_id}", response_model=Item)
def update_item(item_id: int, updated_item: Item):
    if item_id < len(items):
        items[item_id] = updated_item
        return updated_item
    else:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")


# Delete an item
@app.delete("/items/{item_id}", response_model=dict)
def delete_item(item_id: int):
    if item_id < len(items):
        removed_item = items.pop(item_id)
        return {"message": "Item deleted successfully", "item": removed_item}
    else:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")


bandss = [
    {'id':1, 'name':'the knights', 'genre':'Rock'},
    {'id':2, 'name':'the knights', 'genre':'Electronics', 'albums':[{'titles':'Mater of reality', 'release_date':'1971-08-21'}]},
    {'id':3, 'name':'the knights', 'genre':'pop'},
    {'id':4, 'name':'the knights', 'genre':'hipo-hop'}
]

@app.get('/bands')
async def bands() -> list[dict]:
    return bandss

@app.get('/bands_new')
async def bands() -> list[Band]:
    return [ Band(**b) for b in bandss]

@app.get('/bands/genre/{genre}')
async def bands_for_genre(genre:GenreURLChoices) -> list[dict]:
    return [ b for b in bandss if b['genre'].lower() == genre.value ]

@app.get('/bands/{band_id}')
async def bands(band_id:int) -> Band:
    band = next((b for b in bandss if b['id'] == band_id), None)
    if band is None:
        raise HTTPException(status_code=404, detail='Band not Found')
    
    return band