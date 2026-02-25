#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# miscellaneous.py

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
import base64
from datetime import datetime

# Third party.
import pandas as pd
from sqlalchemy import inspect
from pandas_to_pydantic import dataframe_to_pydantic

# Custom.
from .database import SessionLocal


# ------------------------------------------- Instances ----------------------------------------------------------


# ------------------------------------------- Functions ----------------------------------------------------------
def get_db():
    """
    Resume: Class constructor.
    Description: Creates an object of the class associating the API Rest
        Credentials and endpoint accordingly to the declared mode.
    Args:

    Returns:
        None
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def query_to_df(obj_list: list) -> pd.DataFrame:
    """
    Resume:
    Description:
    Args:
        obj_list (list):


    Returns:
        tuple:
    """
    result = []
    keys: list = []
    for obj in obj_list:
        instance = inspect(obj)
        keys = instance.attrs.keys()
        items = instance.attrs.items()
        result.append([x.value for _, x in items])

    result_dataframe: pd.DataFrame = pd.DataFrame.from_records(result, columns=keys)

    return result_dataframe


def hash_password(password: str) -> str:
    hashed_password: str = base64.b64encode(
        password.encode('UTF-8')).decode('UTF-8')

    return hashed_password


def parse_internal_id(
        internal_id: str
) -> tuple:
    if internal_id.count('-') != 2:
        return False, False, False

    id_service, line_service, user_service = internal_id.split(sep='-')

    try:
        id_service = int(id_service)
    except ValueError:
        pass

    return id_service, line_service, user_service


def data_to_model(data_to_cast: pd.DataFrame, model_cast):
    return dataframe_to_pydantic(data=data_to_cast, model=model_cast)


def log_out(*, message: str, identifier: str = 'X') -> None:
    """
    Resume: Print a message along with the current timestamp.
    Description: This function receives a message to be shown in console along
        with the timestamp.
    Args:
        message (str): Text to be displayed.
        identifier (str): Symbol to be put between brackets to make it easier to
            identify a specific message.

    Returns:
        None
    """
    dt_log: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]
    print(f'{dt_log} - [{identifier}] {message}')

# End-of-file (EOF)
