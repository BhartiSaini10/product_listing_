from django.http import HttpResponse
import urllib
import json
from rest_framework.views import APIView

#Connecting the test database made by me
from pymongo import MongoClient
a = "mongodb+srv://BHARTI:" + urllib.parse.quote("mongo@123") + "@cluster0.99ctsps.mongodb.net/?retryWrites=true&w=majority"
cluster = MongoClient(a)
db = cluster["test_db"]
collection = db["men_tshirts"]

#some constants
DEFAULT_STATUS_CODE = "failure"
SUCCESS_STATUS_CODE = "success"

def index(request):
    return HttpResponse("Hello, world. You're at the myntra index.")

def prettify_response(response=dict()):
    import datetime
    for resp in response:
        for d, v in resp.items():
            if isinstance(v, (datetime.date, datetime.datetime)):
                resp[d] = v.isoformat()
    return response

class GetMensTshirts(APIView):
    def get(self, request):
        requested_data = request.query_params
        response = {
            "response": {},
            "status": DEFAULT_STATUS_CODE,
            "error": ""
        }

        def get_typcasted_query_params(request_data):
            typecasted_data = dict()
            try:
                typecasted_data["page"] = int(request_data.get('page')) if request_data.get(
                    'page') else 1
                typecasted_data["page_limit"] = int(
                    request_data.get('page_limit')) if request_data.get('page_limit') else 4
                typecasted_data["category_name"] = request_data.get("category_name") if request_data.get(
                    "category_name") else None
                typecasted_data["brand_name"] = request_data.get("brand_name") if request_data.get(
                    "brand_name") else None
                typecasted_data["price_range"] = request_data.get("price_range") if request_data.get(
                    "price_range") else None
                typecasted_data["colour_code"] = request_data.get("colour_code") if request_data.get(
                    "colour_code") else None
                typecasted_data["discount"] = float(request_data.get('discount')) if request_data.get(
                    'discount') else None
                typecasted_data["sort"] = str(request_data.get("sort")).lower() if request_data.get(
                    "sort") else "recommended"
            except Exception as e:
                return str(e)
            return typecasted_data

        typecasted_data = get_typcasted_query_params(requested_data)
        if isinstance(typecasted_data, str):
            response["error"] = typecasted_data
            return HttpResponse(json.dumps(response))

        offset = None
        limit = None
        if typecasted_data["page"] and typecasted_data["page_limit"]:
            offset = (typecasted_data["page"] - 1) * typecasted_data["page_limit"]
            limit = typecasted_data["page_limit"]

        filter_kwargs = dict()
        if typecasted_data["category_name"]:
            filter_kwargs["category_name"] = typecasted_data["category_name"]
        if typecasted_data["brand_name"]:
            filter_kwargs["brand_name"] = {"$regex": typecasted_data["brand_name"], "$options": "i"}
        if typecasted_data["price_range"]:
            price_range = typecasted_data["price_range"].split("-")
            min_price, max_price = price_range[0], price_range[1]
            try:
                filter_kwargs["price"] = {
                    '$gte': float(min_price), '$lte': float(max_price)
                }
            except:
                response["error"] = "Enter valid price range"
                return HttpResponse(json.dumps(response))
        if typecasted_data["colour_code"]:
            filter_kwargs["colour_code"] = typecasted_data["colour_code"]
        if typecasted_data["discount"] or typecasted_data["discount"]==0:
            try:
                filter_kwargs["discount"] = {
                    '$gte': typecasted_data["discount"]
                }
            except:
                response["error"] = "Enter valid discount"
                return HttpResponse(json.dumps(response))
        if typecasted_data["sort"] in ["recommended", "popularity"]:
            sort = {
                "popularity": 1
            }
        elif typecasted_data["sort"] == "new":
            sort = {
                "created_at": -1
            }
        elif typecasted_data["sort"] == "discount":
            sort = {
                "discount": -1
            }
        elif typecasted_data["sort"] == "price_desc":
            sort = {
                "price": -1
            }
        elif typecasted_data["sort"] == "price_asc":
            sort = {
                "price": 1
            }
        elif typecasted_data["sort"] == "customer_rating":
            sort = {
                "rating": -1
            }
        else:
            sort = {
                "popularity": 1
            }
        pipeline_1 = [
            {
                "$match": filter_kwargs
            },
            {"$project": {"_id": 0}}
        ]
        pipeline_1.append({
            "$sort": sort
        })
        if offset:
            pipeline_1.append({
                '$skip': offset
            })
        if limit:
            pipeline_1.append({
                '$limit': limit
            })
        print(pipeline_1, "pipeline")
        result = list(collection.aggregate(pipeline_1))
        if not result:
            response["error"] = "No results found"
            return HttpResponse(json.dumps(response))

        response["status"] = SUCCESS_STATUS_CODE
        response["response"] = prettify_response(result)
        return HttpResponse(json.dumps(response))

