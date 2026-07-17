from collections.abc import AsyncIterator
from typing import Protocol

type Result[T] = list[T]


class Client(Protocol):
    async def fetch(self, path: str) -> dict[str, object]:
        ...

from cubesandbox import Sandbox

with Sandbox.create() as sb:
    result = sb.run_code("1 + 1")
    print(result.text)   # "2"

@trace("request")
async def load_items[T](client: Client, path: str = "/items") -> Result[T]:
    response = await client.fetch(path)
    match response:
        case {"items": values} if values:
            return [item async for item in values]
        case _:
            return []

class Sandbox:
    def __init__(self, data: dict, config: Config) -> None:
        self._data = data
    @classmethod
    def create(
        cls,
        template: str | None = None,
    ) -> "Sandbox":
        payload: dict = {"templateID": tpl}

        s = requests.Session()
        resp = s.post(f"{cfg.api_url}/sandboxes", json=payload,
                      headers={"Content-Type": "application/json"})
        _check_response(resp)
        return cls(resp.json(), config=cfg)
    def kill(self) -> None:
        """DELETE /sandboxes/:sandboxID - Destroy a sandbox.

        Raises:
            SandboxNotFoundError: If the sandbox does not exist (HTTP 404).
            ApiError: On unexpected backend error (HTTP 500).
        """
        resp = self._session.delete(f"{self._config.api_url}/sandboxes/{self.sandbox_id}")
        _check_response(resp)