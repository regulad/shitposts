from typing import Optional, Iterable, List, Dict, Union, Mapping
from json import dumps
from functools import wraps

from aiohttp import ClientSession, ClientResponse, FormData

from .errors import *
from ._endpoint import *


def process_resp(resp: ClientResponse) -> None:
    if resp.ok:
        return None
    elif resp.status == 429:
        raise RatelimitException(resp=resp)
    else:
        raise HTTPException(resp.reason, status_code=resp.status)


def async_require_session(func):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        if self._client_session:
            return await func(self, *args, **kwargs)
        else:
            raise NoInitialisedSession

    return wrapper


class AsyncShitpostingSession:
    def __init__(self, endpoint: str = ENDPOINT, *, client_session: Optional[ClientSession] = None):
        self.endpoint = endpoint
        self._client_session = client_session
        self._client_session_is_passed = self._client_session is not None

    async def __aenter__(self):
        if not self._client_session_is_passed:
            self._client_session = ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if not self._client_session_is_passed:
            await self._client_session.close()

    @async_require_session
    async def edit(
            self,
            input_media: bytes,
            media_type: str,
            edits: Iterable[Mapping[str, Union[str, Mapping[str, str]]]]
    ) -> bytes:
        """Edit bytes using the /edit endpoint.

        You must specify valid MIME type in the media_type argument.

        If the request is a success, the return type will be the same that was requested."""

        form = FormData()

        form.add_field("Media", input_media, content_type=media_type)
        form.add_field("Edits", dumps({"edits": edits}), content_type="application/json")

        async with self._client_session.post(f"{self.endpoint}edit", data=form) as resp:
            process_resp(resp)

            return await resp.read()

    @async_require_session
    async def user(self) -> dict:
        """Retrieve user stats from the /user endpoint."""

        async with self._client_session.get(f"{self.endpoint}user") as resp:
            process_resp(resp)

            return await resp.json()

    @async_require_session
    async def commands(self) -> List[Dict[str, Union[str, List[Dict[str, str]]]]]:
        """Get video-editing commands that the server can execute."""

        async with self._client_session.get(f"{self.endpoint}commands") as resp:
            process_resp(resp)

            try:
                return (await resp.json())["commands"]
            except KeyError:
                raise UnknownResponse(resp=resp)
            except Exception:
                raise


__all___ = ["AsyncShitpostingSession"]
