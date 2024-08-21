import json
from pydantic import BaseModel
from fastapi import APIRouter, Response
from search.utils.schema import document_class
from search.utils.weaviate_utils import WeaviateClient

class GeoCoordinates(BaseModel):
    latitude: float
    longitude: float

class Place(BaseModel):

    place_name: str
    address: str
    location: GeoCoordinates
    tag: str


router = APIRouter()
weaviateConnection = WeaviateClient()
weaviateConnection.initiate_database(schema=document_class)

@router.post('/search_duplicate')
def get_duplicates(request: Place):
    error =[]
    try:
        
        result = weaviateConnection.search_near_geo_raw("Document", request)
        
        
    except Exception as e:
        error = e
    if error:
        response_content, response_status = error, 501

    else:
        response_content, response_status = result, 200

    return Response(
        content=json.dumps(response_content),
        status_code=response_status,
        media_type="application/json")
