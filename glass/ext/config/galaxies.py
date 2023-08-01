# author: Nicolas Tessore <n.tessore@ucl.ac.uk>
# license: MIT
"""GLASS configuration for galaxies."""

from __future__ import annotations

from . import ArrayLike, Config


def dndz_from_config(config: Config) -> ArrayLike:
    _dndz = config.getep("galaxies.dndz")
    return _dndz(config)


def gaussian_dndz_from_config(config: Config) -> ArrayLike:
    from glass.observations import gaussian_nz
    z = config.getrange("galaxies.dndz.z")
    mean = config.getarray(float, "galaxies.dndz.median")
    sigma = config.getarray(float, "galaxies.dndz.sigma")
    norm = config.getarray(float, "galaxies.ngal")
    return z, gaussian_nz(z, mean, sigma, norm=norm)
