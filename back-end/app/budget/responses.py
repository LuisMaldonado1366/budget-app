#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# responses.py

"""
Description:
Author: Luis Maldonado.
Created on:
Modified on:
Version: 1.0.0
Dependencies:
"""


# ------------------------------------------- Classes ----------------------------------------------------------
class Responses:
    call_id: dict[int, str] = {
        404: {'description': 'Service: Not Found'},
        401: {'description': 'Not authenticated'}
    }

    calls: dict[int, str] = {
        401: {'description': 'Not authenticated'},
        500: {"description": "Internal server error, Error processing request"}
    }

# End-of-file (EOF)
