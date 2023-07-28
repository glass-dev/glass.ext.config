# author: Nicolas Tessore <n.tessore@ucl.ac.uk>
# license: MIT
"""GLASS configuration for shells"""

from __future__ import annotations

from typing import Any, Callable

from . import ArrayLike, Config, ConfigError, Cosmology, RadialWindow


def grid_from_config(config: Config,
                     cosmo: Cosmology | None = None,
                     ) -> ArrayLike:
    _grid = config.getep("shells.grid")
    return _grid(config, cosmo)


def distance_grid_from_config(config: Config,
                              cosmo: Cosmology | None = None,
                              ) -> ArrayLike:
    from glass.shells import distance_grid
    if cosmo is None:
        exc = ConfigError("comoving distance grid requires cosmology")
        exc.add_note("Setting 'shells.grid' to 'distance' requires a "
                     "cosmology.")
        raise exc
    zmin = config.getfloat("shells.grid.zmin", 0.)
    zmax = config.getfloat("shells.grid.zmax")
    dx = config.getfloat("shells.grid.dx", None)
    num = config.getint("shells.grid.num", None)
    return distance_grid(cosmo, zmin, zmax, dx=dx, num=num)


def weight_from_config(config: Config,
                       cosmo: Cosmology | None = None,
                       ) -> Callable[[ArrayLike], ArrayLike]:
    _weight = config.getep("shells.weight", optional=True)
    return _weight(config, cosmo)


def tophat_shells_from_config(config: Config,
                              cosmo: Cosmology | None = None,
                              weight: Any | None = None,
                              ) -> list[RadialWindow]:
    from glass.shells import tophat_windows
    grid = grid_from_config(config, cosmo)
    if "shells.weight" in config:
        weight = weight_from_config(config, cosmo)
    else:
        weight = None
    return tophat_windows(grid, weight=weight)
