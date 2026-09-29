from __future__ import annotations

import os
from collections.abc import Mapping, Sequence
from functools import cache
from typing import Any, BinaryIO, TypeAlias, TypeVar, get_origin, overload

import httpx
from pydantic import BaseModel, TypeAdapter

from .errors import FortniteAPIError

DEFAULT_BASE_URL = "https://prod.api-fortnite.com/api"

FileInput: TypeAlias = bytes | bytearray | BinaryIO | str
"""A replay file: raw bytes, an open binary file object, or a filesystem path."""

FileTuple: TypeAlias = tuple[str, bytes, str]
MultipartFiles: TypeAlias = Mapping[str, FileTuple] | Sequence[tuple[str, FileTuple]]

T = TypeVar("T")


@cache
def _adapter(response_type: Any) -> TypeAdapter[Any]:
    return TypeAdapter(response_type)


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
        self.root_url = self.base_url.removesuffix("/api")
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
    def _clean(params: Mapping[str, Any] | None) -> dict[str, Any] | None:
        if not params:
            return None
        cleaned = {k: v for k, v in params.items() if v is not None}
        return cleaned or None

    @staticmethod
    def _error(resp: httpx.Response) -> FortniteAPIError:
        try:
            data: Any = resp.json()
        except ValueError:
            data = {"error": "Request failed"}
        message = None
        if isinstance(data, dict):
            message = data.get("error") or data.get("title") or data.get("detail")
        return FortniteAPIError(message or f"Request failed with status {resp.status_code}", resp.status_code, data)

    @staticmethod
    def _parse(data: Any, response_type: Any = None) -> Any:
        """Validate ``data`` against ``response_type`` (a model, ``list[Model]``, ``dict[str, ...]``...).

        ``None`` returns the raw JSON untouched. For list types, a dict holding exactly one
        list value (e.g. ``{"status": 200, "patches": [...]}``) is unwrapped to that list.
        """
        if response_type is None:
            return data
        if get_origin(response_type) is list and isinstance(data, dict):
            lists = [v for v in data.values() if isinstance(v, list)]
            if len(lists) == 1:
                data = lists[0]
        return _adapter(response_type).validate_python(data)

    @staticmethod
    def _body(body: Any) -> Any:
        """Serialise request bodies: pydantic models are dumped by alias without ``None`` fields."""
        if isinstance(body, BaseModel):
            return body.model_dump(mode="json", by_alias=True, exclude_none=True)
        if isinstance(body, (list, tuple)):
            return [_BaseTransport._body(item) for item in body]
        return body

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
    def _file_tuple(file: FileInput, filename: str | None) -> FileTuple:
        if isinstance(file, str):
            with open(file, "rb") as handle:
                content = handle.read()
            name = filename or os.path.basename(file)
        elif isinstance(file, (bytes, bytearray)):
            content = bytes(file)
            name = filename or "replay.replay"
        else:
            content = file.read()
            name = filename or str(getattr(file, "name", "replay.replay"))
        return (name, content, "application/octet-stream")

    def _json_result(self, resp: httpx.Response, response_type: Any, *, unwrap: bool = True) -> Any:
        if not resp.is_success:
            raise self._error(resp)
        data = resp.json()
        return self._parse(self._unwrap(data) if unwrap else data, response_type)

    def _binary_result(self, resp: httpx.Response) -> bytes:
        if not resp.is_success:
            raise self._error(resp)
        return resp.content

    def _redirect_result(self, resp: httpx.Response) -> str | None:
        if resp.is_redirect:
            location: str | None = resp.headers.get("location")
            return location
        if resp.is_success:
            return str(resp.url)
        raise self._error(resp)


class SyncTransport(_BaseTransport):
    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 30.0,
        fortnite_token: str | None = None,
    ) -> None:
        super().__init__(api_key, base_url, timeout, fortnite_token)
        self._client = httpx.Client(timeout=self.timeout, follow_redirects=True)

    def close(self) -> None:
        self._client.close()

    @overload
    def request(
        self,
        method: str,
        path: str,
        version: str | None,
        *,
        params: Mapping[str, Any] | None = ...,
        json_body: Any = ...,
        fortnite_token: str | None = ...,
        response_type: None = ...,
    ) -> Any: ...

    @overload
    def request(
        self,
        method: str,
        path: str,
        version: str | None,
        *,
        params: Mapping[str, Any] | None = ...,
        json_body: Any = ...,
        fortnite_token: str | None = ...,
        response_type: type[T],
    ) -> T: ...

    def request(
        self,
        method: str,
        path: str,
        version: str | None,
        *,
        params: Mapping[str, Any] | None = None,
        json_body: Any = None,
        fortnite_token: str | None = None,
        response_type: Any = None,
    ) -> Any:
        resp = self._client.request(
            method,
            self._url(path, version),
            params=self._clean(params),
            json=self._body(json_body),
            headers=self._headers(fortnite_token),
        )
        return self._json_result(resp, response_type)

    def request_binary(self, path: str, version: str | None, *, fortnite_token: str | None = None) -> bytes:
        resp = self._client.get(self._url(path, version), headers=self._headers(fortnite_token, json=False))
        return self._binary_result(resp)

    def request_redirect(
        self,
        path: str,
        version: str | None,
        *,
        params: Mapping[str, Any] | None = None,
        fortnite_token: str | None = None,
    ) -> str | None:
        resp = self._client.get(
            self._url(path, version),
            params=self._clean(params),
            headers=self._headers(fortnite_token, json=False),
            follow_redirects=False,
        )
        return self._redirect_result(resp)

    @overload
    def request_multipart(
        self, path: str, files: MultipartFiles, *, response_type: None = ..., unwrap: bool = ...
    ) -> Any: ...

    @overload
    def request_multipart(
        self, path: str, files: MultipartFiles, *, response_type: type[T], unwrap: bool = ...
    ) -> T: ...

    def request_multipart(
        self, path: str, files: MultipartFiles, *, response_type: Any = None, unwrap: bool = True
    ) -> Any:
        resp = self._client.post(self._url(path, "v1"), headers=self._headers(None, json=False), files=files)
        return self._json_result(resp, response_type, unwrap=unwrap)


class AsyncTransport(_BaseTransport):
    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 30.0,
        fortnite_token: str | None = None,
    ) -> None:
        super().__init__(api_key, base_url, timeout, fortnite_token)
        self._client = httpx.AsyncClient(timeout=self.timeout, follow_redirects=True)

    async def close(self) -> None:
        await self._client.aclose()

    @overload
    async def request(
        self,
        method: str,
        path: str,
        version: str | None,
        *,
        params: Mapping[str, Any] | None = ...,
        json_body: Any = ...,
        fortnite_token: str | None = ...,
        response_type: None = ...,
    ) -> Any: ...

    @overload
    async def request(
        self,
        method: str,
        path: str,
        version: str | None,
        *,
        params: Mapping[str, Any] | None = ...,
        json_body: Any = ...,
        fortnite_token: str | None = ...,
        response_type: type[T],
    ) -> T: ...

    async def request(
        self,
        method: str,
        path: str,
        version: str | None,
        *,
        params: Mapping[str, Any] | None = None,
        json_body: Any = None,
        fortnite_token: str | None = None,
        response_type: Any = None,
    ) -> Any:
        resp = await self._client.request(
            method,
            self._url(path, version),
            params=self._clean(params),
            json=self._body(json_body),
            headers=self._headers(fortnite_token),
        )
        return self._json_result(resp, response_type)

    async def request_binary(self, path: str, version: str | None, *, fortnite_token: str | None = None) -> bytes:
        resp = await self._client.get(self._url(path, version), headers=self._headers(fortnite_token, json=False))
        return self._binary_result(resp)

    async def request_redirect(
        self,
        path: str,
        version: str | None,
        *,
        params: Mapping[str, Any] | None = None,
        fortnite_token: str | None = None,
    ) -> str | None:
        resp = await self._client.get(
            self._url(path, version),
            params=self._clean(params),
            headers=self._headers(fortnite_token, json=False),
            follow_redirects=False,
        )
        return self._redirect_result(resp)

    @overload
    async def request_multipart(
        self, path: str, files: MultipartFiles, *, response_type: None = ..., unwrap: bool = ...
    ) -> Any: ...

    @overload
    async def request_multipart(
        self, path: str, files: MultipartFiles, *, response_type: type[T], unwrap: bool = ...
    ) -> T: ...

    async def request_multipart(
        self, path: str, files: MultipartFiles, *, response_type: Any = None, unwrap: bool = True
    ) -> Any:
        resp = await self._client.post(self._url(path, "v1"), headers=self._headers(None, json=False), files=files)
        return self._json_result(resp, response_type, unwrap=unwrap)
