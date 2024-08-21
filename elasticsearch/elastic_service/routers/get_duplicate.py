import json
from pydantic import BaseModel
from fastapi import APIRouter, Response
from search.utils.schema import index_name, body
from search.utils.elastic_utils import ElasticClient

class Place(BaseModel):

    place_name: str
    location: str
    address: str
    tag: str


router = APIRouter()
elasticConnection = ElasticClient()
elasticConnection.initiate_database(index_name=index_name, body=body)


@router.post('/search_duplicate')
def get_duplicates(request: Place):
    error =[]
    try:
        
        result = elasticConnection.multi_match_search(index_name, request)
        
        
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
