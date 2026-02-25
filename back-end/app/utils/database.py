#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# database.py

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

# Third party.
from sqlalchemy import create_engine, URL
# noinspection PyUnresolvedReferences
from sqlalchemy.orm import sessionmaker
# noinspection PyUnresolvedReferences
from sqlalchemy.ext.declarative import declarative_base

# Custom.
from config import Config


# ------------------------------------------- Instances ----------------------------------------------------------
SQLALCHEMY_DATABASE_URL = URL.create(drivername=Config.SQL_DRIVER,
                                     username=Config.DB_USER,
                                     password=Config.DB_PASSWORD,
                                     host=Config.DB_HOST,
                                     port=Config.DB_PORT,
                                     database=Config.DB_NAME)

engine = create_engine(url=SQLALCHEMY_DATABASE_URL,
                       pool_pre_ping=True,
                       pool_recycle=300)
SessionLocal: sessionmaker = sessionmaker(autoflush=False, bind=engine)
Base = declarative_base()

# End-of-file (EOF)
