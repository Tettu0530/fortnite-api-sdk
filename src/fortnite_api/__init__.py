from __future__ import annotations

from . import models
from .client import AsyncFortniteAPI, FortniteAPI
from .errors import FortniteAPIError

__version__ = "0.1.1"

__all__ = ["FortniteAPI", "AsyncFortniteAPI", "FortniteAPIError", "models", "__version__"]
