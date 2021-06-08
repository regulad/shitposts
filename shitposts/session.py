from typing import Iterable, List, Dict, Union, Mapping
from json import dumps
from functools import wraps

import requests
from requests_toolbelt import MultipartEncoder

from .errors import *
from ._endpoint import *


def process_resp(resp: requests.Response) -> None:
    if resp.ok:
        return None
    elif resp.status_code == 429:
        raise RatelimitException
    else:
        raise HTTPException(resp.reason, status_code=resp.status_code)


class ShitpostingSession:
    def __init__(self, endpoint: str = ENDPOINT):
        self.endpoint = endpoint

    def edit(
            self,
            input_media: bytes,
            media_type: str,
            edits: Iterable[Mapping[str, Union[str, Mapping[str, str]]]]
    ) -> bytes:
        """Edit bytes using the /edit endpoint.

        You must specify valid MIME type in the media_type argument.

        If the request is a success, the return type will be the same that was requested."""

        edits_json = dumps({"edits": edits})

        form = MultipartEncoder(
            {
                "Media": ("", input_media, media_type),
                "Edits": edits_json,
            }
        )

        with requests.post(f"{self.endpoint}edit", data=form, headers={"Content-Type": form.content_type}) as resp:
            process_resp(resp)

            return resp.content

    def user(self) -> dict:
        """Retrieve user stats from the /user endpoint."""

        with requests.get(f"{self.endpoint}user") as resp:
            process_resp(resp)

            return resp.json()

    def commands(self) -> List[Dict[str, Union[str, List[Dict[str, str]]]]]:
        """Get video-editing commands that the server can execute."""

        with requests.get(f"{self.endpoint}commands") as resp:
            process_resp(resp)

            try:
                return resp.json()["commands"]
            except KeyError:
                raise UnknownResponse(resp=resp)
            except Exception:
                raise


__all___ = ["ShitpostingSession"]
