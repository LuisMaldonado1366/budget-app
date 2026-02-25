#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# errors.py

"""
Description:
Author: Luis Maldonado.
Created on:
Modified on:
Version: 1.0.0
Dependencies:
"""
import binascii
# ------------------------------------------- Libraries ----------------------------------------------------------
from ssl import SSLCertVerificationError
from socket import gaierror
# noinspection PyUnresolvedReferences
from sqlalchemy.exc import IntegrityError, OperationalError, ProgrammingError, DataError
from pymysql import OperationalError as pymysqlOperationalError
from http.client import RemoteDisconnected, InvalidURL
from requests.exceptions import ReadTimeout, ConnectTimeout

# -------------------------------------------- Epicor ------------------------------------------------------------
DB_ERRORS = (IntegrityError, OperationalError, pymysqlOperationalError, ProgrammingError, DataError)
LOGIN_ERRORS: tuple = (binascii.Error, UnicodeDecodeError)

# End-of-file (EOF)
