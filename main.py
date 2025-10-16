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

from fastapi import FastAPI, HTTPException,Query, Depends,Path
from pydantic import BaseModel
from schemas import GenreURLChoices, BandBase, BandCreate, BandWithId, Albums,AlbumBase
from enum import Enum
from typing import Annotated
from contextlib import asynccontextmanager
from db import init_db, get_session
from sqlmodel import Session, select    

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)




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
    {'id':2, 'name':'the knights', 'genre':'Electronics', 'albums':[{'title':'Mater of reality', 'release_date':'1971-08-21'}]},
    {'id':3, 'name':'the knights', 'genre':'pop'},
    {'id':4, 'name':'the knights', 'genre':'hipo-hop'}
]

@app.get('/bands')
async def bands(genre: GenreURLChoices | None = None, has_albums: bool = False) -> list[BandBase]:
    # Ensure all items in `bandss` have the required fields
    band_list = [BandBase(**b) for b in bandss if 'genre' in b and 'albums' in b]

    # Filter by genre if provided
    if genre:
        band_list = [b for b in band_list if b.genre.lower() == genre.value.lower()]

    # Filter by albums if has_albums is True
    if has_albums:
        band_list = [b for b in band_list if len(b.albums) > 0]

    return band_list


@app.get('/bands_new')
async def bands() -> list[BandBase]:
    return [ BandBase(**b) for b in bandss]

@app.get('/bands/genre/{genre}')
async def bands_for_genre(genre:GenreURLChoices | None = None, q:Annotated[str | None, Query(max_length=10)] = None, ) -> list[BandWithId ]:
    return [ b for b in bandss if b['genre'].lower() == genre.value ]

@app.get('/bands/{band_id}')
async def bands(band_id:Annotated[int, Path(title="The Band Id")],
                session:Session = Depends(get_session)) -> BandBase:
    band = session.get(BandBase, band_id)
    if band is None:
        raise HTTPException(status_code=404, detail='Band not Found')
    
    return band


# @app.post("/bands")
# async def create_band(band_data: BandCreate) -> BandWithId:
#     id  = bandss[-1]['id'] + 1
#     print('idddddd', id)
#     band = BandWithId(id=id, **band_data.model_dump()).model_dump()
#     bandss.append(band)
#     return band

@app.post("/bands")
async def create_band(band_data: BandCreate, session:Session = Depends(get_session)) -> BandBase:

    band = BandBase(name=band_data.name, genre=band_data.genre)
    session.add(band)
    if band_data.albums:
        for album in band_data.albums:
            album_obj = Albums(title=album.title, release_date=album.release_date, band=band)
            session.add(album_obj)
    session.commit()
    session.refresh(band)

    # Return the new band
    return band
