from __future__ import annotations

import functools
import inspect
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable
    from types import ModuleType
    from typing import Any

logger = logging.getLogger(__name__)


def log_io(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator that logs function input arguments and return value at DEBUG level."""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        qualname = func.__qualname__
        logger.debug("%s called with args=%r kwargs=%r", qualname, args, kwargs)
        result = func(*args, **kwargs)
        logger.debug("%s returned %r", qualname, result)
        return result

    return wrapper


def apply_logging(module: ModuleType) -> None:
    """Wrap all public functions defined in *module* with the :func:`log_io` decorator.

    Only functions whose ``__module__`` matches the target module are wrapped,
    so re-exported imports are left untouched.
    """
    for name in dir(module):
        if name.startswith("_"):
            continue
        attr = getattr(module, name)
        if (
            inspect.isfunction(attr)
            and getattr(attr, "__module__", None) == module.__name__
        ):
            setattr(module, name, log_io(attr))
