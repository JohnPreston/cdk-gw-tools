# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 John Mille <john@ews-network.net>

from __future__ import annotations

from requests import Response


def format_return(function):
    """
    Decorator to evaluate the requests payload returned
    """

    def wrapped_answer(*args, **kwargs):
        """
        Decorator wrapper
        """
        req = function(*args, **kwargs)
        if isinstance(req, Response):
            try:
                return req.json()
            except Exception as error:
                print("request response not in JSON")
                print(error)
                return req.text
        return req

    return wrapped_answer
