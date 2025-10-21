from fastapi import FastAPI
from routers import building, activity, organization

app = FastAPI(debug=False)

app.include_router(building.router)
app.include_router(activity.router)
app.include_router(organization.router)


