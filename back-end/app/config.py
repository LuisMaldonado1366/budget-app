#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# config.py

"""
Description:
Author: Luis Maldonado.
Created on:
Modified on:
Version: 1.0.0
Dependencies:
"""
# ------------------------------------------- Libraries ----------------------------------------------------------
# Standard
from pydantic_settings import BaseSettings, SettingsConfigDict

# ----------------------------------------- Environment ---------------------------------------------------------
class Settings(BaseSettings):
    ENVIRONMENT: str

    # API SETTINGS
    API_PORT: int = 3000
    API_TITLE: str
    API_VERSION: str
    END_POINT: str
    WEB_URL: str

    # SWAGGER SETTINGS
    DOCS_USER_NAME: str
    DOCS_PASSWORD: str

    # TOKEN SETTINGS
    TOKEN_SIGNATURE: str
    TOKEN_ISSUER: str
    TOKEN_EXPIRATION_HRS: int
    TOKEN_REFRESH_EXPIRATION_HRS: int
    TOKEN_ALGORITHM: str
    QR_SIGNATURE: str

    # DB SETTINGS
    SQL_DRIVER: str
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str


    model_config = SettingsConfigDict(
        env_file='../.env',
        extra='ignore'
    )


Config = Settings()
