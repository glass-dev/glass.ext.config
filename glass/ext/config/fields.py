# author: Nicolas Tessore <n.tessore@ucl.ac.uk>
# license: MIT
"""GLASS configuration for fields"""

from __future__ import annotations

from . import ArrayLike, Config, ConfigError, Cosmology, RadialWindow


def load_cls_from_config(config: Config,
                         shells: list[RadialWindow],
                         cosmo: Cosmology | None = None,
                         ) -> list[ArrayLike]:
    from glass.user import load_cls
    try:
        cls_path = config.getstr("fields.cls.path")
    except ConfigError as exc:
        exc.add_note("The 'fields.cls.path' option is required if "
                     "'fields.cls' is set to 'load'.")
        raise
    cls = load_cls(cls_path)
    if len(cls) != len(shells)*(len(shells)+1)//2:
        raise ConfigError("loaded cls do not match shells")
    return cls
