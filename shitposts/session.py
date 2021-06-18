from functools import wraps
from json import dumps
from typing import Optional, List, Dict, Union, Mapping

from aiohttp import ClientSession, ClientResponse, FormData

from .errors import *

ENDPOINT = "https://shitposts.local.regulad.xyz/v1/"


def process_resp(resp: ClientResponse) -> None:
    if resp.ok:
        return None
    elif resp.status == 429:
        raise RatelimitException(resp.reason)
    else:
        raise HTTPException(resp.reason, status_code=resp.status)


def require_session(func):
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

    @require_session
    async def edit(self, input_media: bytes, media_type: str, **kwargs) -> bytes:
        """Edit bytes using the /edit endpoint.

        You must specify valid MIME type in the media_type argument.

        If the request is a success, the return type will be the same that was requested."""

        edits = []

        for kwarg, value in kwargs.items():
            edits.append(
                {
                    "name": kwarg,
                    "parameters": value,
                }
            )

        edit_dict = {"edits": edits}

        form = FormData()

        form.add_field("Media", input_media, content_type=media_type)
        form.add_field("Edits", dumps(edit_dict), content_type="application/json")

        async with self._client_session.post(f"{self.endpoint}edit", data=form) as resp:
            process_resp(resp)

            return await resp.read()

    @require_session
    async def user(self) -> dict:
        """Retrieve user stats from the /user endpoint."""

        async with self._client_session.get(f"{self.endpoint}user") as resp:
            process_resp(resp)

            return await resp.json()

    @require_session
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

    @require_session
    async def get_command(self, command_name: str) -> Dict[str, Union[str, List[Dict[str, str]]]]:
        """Get a single command from the server."""

        async with self._client_session.get(f"{self.endpoint}commands/{command_name}") as resp:
            process_resp(resp)

            return await resp.json()


__all___ = ["AsyncShitpostingSession"]
