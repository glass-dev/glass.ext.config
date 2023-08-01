# author: Nicolas Tessore <n.tessore@ucl.ac.uk>
# license: MIT
"""GLASS configuration backend"""

from __future__ import annotations

__all__ = (
    "Config",
    "ConfigError",
    "cls_from_config",
    "cosmo_from_config",
    "shells_from_config",
)

import sys
from collections import UserDict
from typing import Any

import numpy as np
from numpy.typing import ArrayLike, DTypeLike

from cosmology import Cosmology
from glass.shells import RadialWindow

if sys.version_info < (3, 10):
    from importlib_metadata import entry_points
else:
    from importlib.metadata import entry_points


class NoDefaultType:
    def __new__(cls) -> NoDefaultType:
        return NoDefault

    def __repr__(self) -> str:
        return "NoDefault"

    def __str__(self) -> str:
        return "<no default>"


NoDefault = object.__new__(NoDefaultType)


class ConfigError(Exception):
    def add_note(self, msg: str) -> None:
        try:
            super().add_note(msg)
        except AttributeError:
            pass


class Config(UserDict):
    def get(self, key: str, default: Any = NoDefault, *,
            converter: type | None = None,
            choices: list[Any] | None = None,
            ) -> Any:
        try:
            value = self.data[key]
        except KeyError as exc:
            if default is not NoDefault:
                return default
            exc = ConfigError(f"{key}: missing option")
            exc.add_note(f"Your configuration is missing the '{key}' option.")
            raise exc from None
        if converter is not None:
            value = converter(value)
        if choices is not None and value not in choices:
            exc = ConfigError(f"{key}: invalid value '{value}'")
            exc.add_note("Valid choices are: " + ", ".join(map(repr, choices)))
            raise exc
        return value

    def getbool(self, key: str,
                default: bool | None | NoDefaultType = NoDefault,
                ) -> bool:
        def converter(value: str) -> bool:
            if value == "true":
                return True
            if value == "false":
                return False
            raise ValueError(f"could not convert string to bool: {value}")

        choices = ["true", "false"]
        return self.get(key, default, converter=converter, choices=choices)

    def getstr(self, key: str,
               default: str | None | NoDefaultType = NoDefault,
               *,
               choices: list[str] | None = None,
               ) -> str:
        return self.get(key, default, converter=str, choices=choices)

    def getint(self, key: str,
               default: int | None | NoDefaultType = NoDefault,
               *,
               choices: list[int] | None = None,
               ) -> int:
        return self.get(key, default, converter=int, choices=choices)

    def getfloat(self, key: str,
                 default: float | None | NoDefaultType = NoDefault,
                 *,
                 choices: list[float] | None = None,
                 ) -> float:
        return self.get(key, default, converter=float, choices=choices)

    def getarray(self, dtype: DTypeLike, key: str,
                 default: ArrayLike | None | NoDefaultType = NoDefault,
                 ) -> ArrayLike:
        def converter(s: str) -> ArrayLike:
            s = s.replace("\n", " ")
            return np.fromstring(s, dtype, sep=",")

        return self.get(key, default, converter=converter)

    def getep(self, key: str, group: str | None = None, *,
              optional: bool = False) -> Any:
        eps = entry_points(group=f"glass.{group or key}")
        choices = [ep.name for ep in eps]
        default = None if optional else NoDefault
        name = self.getstr(key, default=default, choices=choices)
        if name is None:
            return name
        ep = next(ep for ep in eps if ep.name == name)
        return ep.load()

    def getrange(self, key: str,
                 default: ArrayLike | None | NoDefaultType = NoDefault,
                 ) -> ArrayLike:
        def converter(s: str) -> ArrayLike:
            try:
                which, start, stop, step = s.split()
            except ValueError:
                raise ConfigError(f"{key}: range must be of the form 'FUNC "
                                  "START STOP STEP'") from None
            if which == "arange":
                step = float(step)
            else:
                step = int(step)
            return getattr(np, which)(float(start), float(stop), step)

        return self.get(key, default, converter=converter)


def cosmo_from_config(config: Config) -> Cosmology:
    _cosmo = config.getep("cosmo.uses", "cosmo")
    return _cosmo(config)


def shells_from_config(config: Config,
                       cosmo: Cosmology | None = None,
                       ) -> list[RadialWindow]:
    _window = config.getep("shells.window", "shells")
    return _window(config, cosmo)


def cls_from_config(config: Config,
                    shells: list[RadialWindow],
                    cosmo: Cosmology | None = None,
                    ) -> list[ArrayLike]:
    _cls = config.getep("fields.cls")
    return _cls(config, shells, cosmo)
