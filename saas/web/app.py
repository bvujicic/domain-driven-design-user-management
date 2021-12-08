import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from saas.core.config import configuration
from saas.database.metadata import start_mappers
from saas.web.controllers import (
    registration_router,
    admin_router,
    authentication_router,
    users_router,
)
from saas.web.ws.endpoints import websocket_router

web_app = FastAPI(title='SaaS REST API')


web_app.add_middleware(
    CORSMiddleware,
    allow_origins=configuration.CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

web_app.include_router(router=registration_router)
web_app.include_router(router=admin_router)
web_app.include_router(router=authentication_router)
web_app.include_router(router=users_router)
web_app.include_router(router=websocket_router)


@web_app.on_event('startup')
def mappers():
    start_mappers()


if __name__ == '__main__':
    uvicorn.run(web_app, host='0.0.0.0', port=8000)
