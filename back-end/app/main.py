#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# main.py

"""
Description:
Author: Luis Maldonado.
Created on:
Modified on:
Version: 1.0.0
Dependencies:
"""
# ------------------------------------------- Libraries ----------------------------------------------------------
# Standard.
import sys
from os.path import split
import secrets

# Third-party.
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import UJSONResponse, FileResponse, JSONResponse
from fastapi.security import HTTPBasicCredentials, HTTPBasic
from starlette import status
from starlette.responses import RedirectResponse, HTMLResponse

# Custom.
import budget.router as budget
from config import Config
from utils.miscellaneous import log_out

# ------------------------------------------- Constants ----------------------------------------------------------
MAX_RETRIES: int = 3
ORIGINS: list[str] = [
    'https://' + Config.END_POINT,
    'http://localhost',
    'http://localhost:8080',
    'https://' + Config.WEB_URL
]
if Config.ENVIRONMENT in ('DEVELOP', 'LOCAL', 'PRODUCTION'):
    ORIGINS.append('*')

API_TITLE_CLEAN: str = Config.API_TITLE.replace('_', ' ')

# ------------------------------------------- Instances ----------------------------------------------------------
app: FastAPI = FastAPI(title=API_TITLE_CLEAN,
                       version=Config.API_VERSION,
                       docs_url=None,
                       redoc_url=None,
                       openapi_url=None,
                       default_response_class=UJSONResponse,
                       root_path='/v1',
                       root_path_in_servers=True,
                       debug=False)
security_app = HTTPBasic()

# noinspection PyTypeChecker
app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# -------------------------------------------- Routers -----------------------------------------------------------
app.include_router(budget.router)

# ------------------------------------------- Functions ----------------------------------------------------------
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(title=API_TITLE_CLEAN,
                                 version=Config.API_VERSION,
                                 routes=app.routes,
                                 description='Description',
                                 summary='Summary')
    openapi_schema['info']['x-logo'] = {
        "url": "https://www.momatt.com/img/momatt-logo.png"
    }

    return openapi_schema


def get_current_username(credentials: HTTPBasicCredentials = Depends(security_app)):
    correct_username = secrets.compare_digest(credentials.username, Config.DOCS_USER_NAME)
    correct_password = secrets.compare_digest(credentials.password, Config.DOCS_PASSWORD)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect user or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


def main() -> None:
    """
    Resume: Main execution loop.
    Description:

    Returns:
        None
    """
    uvicorn.config.LOGGING_CONFIG['formatters']['default']['fmt'] = \
        '%(asctime)s - [x] %(name)s %(levelprefix)s %(message)s'
    uvicorn.config.LOGGING_CONFIG['formatters']['access']['fmt'] = \
        '%(asctime)s - [x] %(name)s %(levelprefix)s %(message)s'

    config: uvicorn.Config = uvicorn.Config(app=app, host='0.0.0.0', port=Config.API_PORT, log_level='info')
    server: uvicorn.Server = uvicorn.Server(config=config)
    server.run()


# --------------------------------------------- Routes -----------------------------------------------------------
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Log the incoming payload
    try:
        log_out(message=f'Validation error for payload. detail: {exc.errors()})', identifier='X')
    except Exception as e:
        log_out(message=f'Could not parse request body. Cause - {e})', identifier='X')

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )

@app.get(path='/', response_class=RedirectResponse, include_in_schema=False)
async def docs():
    return RedirectResponse(url='/docs')


@app.get(path='/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse('./img/favicon.ico')


@app.get(path="/docs", response_class=HTMLResponse, include_in_schema=False)
async def get_docs(username: str = Depends(get_current_username)):
    if username is not None:
        return get_swagger_ui_html(
            openapi_url="/openapi.json",
            title=API_TITLE_CLEAN,
            swagger_favicon_url='/favicon.ico'
        )
    return None


@app.get(path="/redoc", response_class=HTMLResponse, include_in_schema=False)
async def get_redoc(username: str = Depends(get_current_username)):
    if username is not None:
        return get_redoc_html(openapi_url="/openapi.json", title=API_TITLE_CLEAN)
    return None


@app.get(path="/openapi.json", include_in_schema=False)
async def openapi(username: str = Depends(get_current_username)):
    if username is not None:
        app.openapi_schema = custom_openapi()
        return app.openapi_schema
    return None


# --------------------------------------------- Main ------------------------------------------------------------
if __name__ == '__main__':
    log_out(message='====== INITIALIZING API SERVICE ======', identifier='~')
    log_out(message=f'-- Environment: {Config.ENVIRONMENT} --', identifier='!')
    RETRIES: int = 0

    while RETRIES < MAX_RETRIES:

        try:
            main()
            sys.exit(0)

        except KeyboardInterrupt:
            log_out(message='Keyboard interruption', identifier='x')
            sys.exit(0)

        except Exception as error:
            result_message: str = f'{error.__class__.__name__}'
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_name: str = split(exc_tb.tb_frame.f_code.co_filename)[1]
            RETRIES += 1
            log_out(message=f'''Exit on error: {result_message} - {error.args})
                        Filename: {file_name} - {exc_tb.tb_lineno}''',
                    identifier='x')

        finally:
            log_out(message='====== FINALIZING API SERVICE ======', identifier='~')

# End-of-file (EOF)
