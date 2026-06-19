from __future__ import annotations

import os
from typing import Any, BinaryIO, Union

import httpx
from pydantic import BaseModel

from .errors import FortniteAPIError

DEFAULT_BASE_URL = "https://prod.api-fortnite.com/api"

FileInput = Union[bytes, bytearray, BinaryIO, str]


class _BaseTransport:
    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 30.0,
        fortnite_token: str | None = None,
    ) -> None:
        if not api_key:
            raise ValueError("api_key is required")
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.root_url = self.base_url[:-4] if self.base_url.endswith("/api") else self.base_url
        self.timeout = timeout
        self.fortnite_token = fortnite_token

    def _url(self, path: str, version: str | None) -> str:
        if version is None:
            return f"{self.root_url}{path}"
        return f"{self.base_url}/{version}{path}"

    def _headers(self, fortnite_token: str | None, json: bool = True) -> dict[str, str]:
        headers = {"x-api-key": self.api_key}
        if json:
            headers["Content-Type"] = "application/json"
        token = fortnite_token or self.fortnite_token
        if token:
            headers["x-fortnite-token"] = token
        return headers

    @staticmethod
    def _clean(params: dict[str, Any] | None) -> dict[str, Any] | None:
        if not params:
            return None
        cleaned = {k: v for k, v in params.items() if v is not None}
        return cleaned or None

    @staticmethod
    def _error(resp: httpx.Response) -> FortniteAPIError:
        try:
            data: Any = resp.json()
        except Exception:
            data = {"error": "Request failed"}
        message = None
        if isinstance(data, dict):
            message = data.get("error") or data.get("title") or data.get("detail")
        return FortniteAPIError(message or f"Request failed with status {resp.status_code}", resp.status_code, data)

    @staticmethod
    def _parse(data: Any, model: type[BaseModel] | None, is_list: bool) -> Any:
        if model is None:
            return data
        if is_list:
            if isinstance(data, dict):
                lists = [v for v in data.values() if isinstance(v, list)]
                if len(lists) == 1:
                    data = lists[0]
            return [model.model_validate(item) for item in data]
        return model.model_validate(data)

    @staticmethod
    def _unwrap(data: Any) -> Any:
        if isinstance(data, dict):
            if "success" in data:
                if not data.get("success"):
                    raise FortniteAPIError(data.get("error") or "Request failed", 422, data)
                if "data" in data:
                    return data["data"]
                if "results" in data:
                    return data["results"]
            elif "data" in data and "status" in data:
                return data["data"]
        return data

    @staticmethod
    def _file_tuple(file: FileInput, filename: str | None) -> tuple[str, bytes, str]:
        if isinstance(file, str):
            with open(file, "rb") as handle:
                content = handle.read()
            name = filename or os.path.basename(file)
        elif isinstance(file, (bytes, bytearray)):
            content = bytes(file)
            name = filename or "replay.replay"
        else:
            content = file.read()
            name = filename or getattr(file, "name", "replay.replay")
        return (name, content, "application/octet-stream")


class SyncTransport(_BaseTransport):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._client = httpx.Client(timeout=self.timeout, follow_redirects=True)

    def close(self) -> None:
        self._client.close()

    def request(
        self,
        method: str,
        path: str,
        version: str | None,
        *,
        params: dict[str, Any] | None = None,
        json_body: Any = None,
        fortnite_token: str | None = None,
        model: type[BaseModel] | None = None,
        is_list: bool = False,
    ) -> Any:
        resp = self._client.request(
            method,
            self._url(path, version),
            params=self._clean(params),
            json=json_body,
            headers=self._headers(fortnite_token),
        )
        if not resp.is_success:
            raise self._error(resp)
        return self._parse(self._unwrap(resp.json()), model, is_list)

    def request_binary(self, path: str, version: str | None, *, fortnite_token: str | None = None) -> bytes:
        resp = self._client.get(self._url(path, version), headers=self._headers(fortnite_token, json=False))
        if not resp.is_success:
            raise self._error(resp)
        return resp.content

    def request_redirect(
        self, path: str, version: str | None, *, params: dict[str, Any] | None = None, fortnite_token: str | None = None
    ) -> str | None:
        resp = self._client.get(
            self._url(path, version),
            params=self._clean(params),
            headers=self._headers(fortnite_token, json=False),
            follow_redirects=False,
        )
        if resp.is_redirect:
            return resp.headers.get("location")
        if resp.is_success:
            return str(resp.url)
        raise self._error(resp)

    def request_multipart(
        self, path: str, files: Any, *, model: type[BaseModel] | None = None, is_list: bool = False, unwrap: bool = True
    ) -> Any:
        resp = self._client.post(self._url(path, "v1"), headers=self._headers(None, json=False), files=files)
        if not resp.is_success:
            raise self._error(resp)
        data = self._unwrap(resp.json()) if unwrap else resp.json()
        return self._parse(data, model, is_list)


class AsyncTransport(_BaseTransport):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._client = httpx.AsyncClient(timeout=self.timeout, follow_redirects=True)

    async def close(self) -> None:
        await self._client.aclose()

    async def request(
        self,
        method: str,
        path: str,
        version: str | None,
        *,
        params: dict[str, Any] | None = None,
        json_body: Any = None,
        fortnite_token: str | None = None,
        model: type[BaseModel] | None = None,
        is_list: bool = False,
    ) -> Any:
        resp = await self._client.request(
            method,
            self._url(path, version),
            params=self._clean(params),
            json=json_body,
            headers=self._headers(fortnite_token),
        )
        if not resp.is_success:
            raise self._error(resp)
        return self._parse(self._unwrap(resp.json()), model, is_list)

    async def request_binary(self, path: str, version: str | None, *, fortnite_token: str | None = None) -> bytes:
        resp = await self._client.get(self._url(path, version), headers=self._headers(fortnite_token, json=False))
        if not resp.is_success:
            raise self._error(resp)
        return resp.content

    async def request_redirect(
        self, path: str, version: str | None, *, params: dict[str, Any] | None = None, fortnite_token: str | None = None
    ) -> str | None:
        resp = await self._client.get(
            self._url(path, version),
            params=self._clean(params),
            headers=self._headers(fortnite_token, json=False),
            follow_redirects=False,
        )
        if resp.is_redirect:
            return resp.headers.get("location")
        if resp.is_success:
            return str(resp.url)
        raise self._error(resp)

    async def request_multipart(
        self, path: str, files: Any, *, model: type[BaseModel] | None = None, is_list: bool = False, unwrap: bool = True
    ) -> Any:
        resp = await self._client.post(self._url(path, "v1"), headers=self._headers(None, json=False), files=files)
        if not resp.is_success:
            raise self._error(resp)
        data = self._unwrap(resp.json()) if unwrap else resp.json()
        return self._parse(data, model, is_list)
