from ninja import NinjaAPI
from farmers.routes import router as farmer_router

api = NinjaAPI()
api.add_router("/farmers/", farmer_router)


