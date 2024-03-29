from datetime import datetime

import numpy as np
import numpy.linalg
import numpy.typing as npt
from geojson_pydantic import Point
from skyfield.api import EarthSatellite, Time, Timescale, load, wgs84
from skyfield.framelib import itrs

from .models import Pass, Satellite


def _unit_vector(v: npt.NDArray) -> npt.NDArray:
    return v / numpy.linalg.norm(v)


class EarthObservationSatelliteModel(EarthSatellite):
    _model: Satellite

    def __init__(
        self,
        model: Satellite,
        ts: Timescale | None = None,
    ):
        name, line1, line2 = model.tle_lines
        super().__init__(line1, line2, name, ts)
        self._model = model

    def passes(
        self,
        start: datetime | Time,
        end: datetime | Time,
        lat: float,
        lon: float,
        alt: float,
        off_nadir_range=tuple[float, float],
    ) -> list[Pass]:
        target = wgs84.latlon(lat, lon, alt)
        start = self.ts.from_datetime(start) if isinstance(start, datetime) else start
        end = self.ts.from_datetime(end) if isinstance(end, datetime) else end
        diff = self - target

        moments, _ = self.find_events(target, start, end, 0)
        passes = []
        for t in moments[1::3]:
            off_nadir = self.off_nadir(t.utc_datetime(), lon, lat, alt)
            if not (off_nadir_range[0] <= off_nadir <= off_nadir_range[1]):
                continue

            topocentric = diff.at(t)
            elevation, azimuth, _ = topocentric.altaz()

            passes.append(
                Pass(
                    type="Feature",
                    geometry=Point(
                        type="Point",
                        coordinates=[lon, lat, alt],
                        bbox=[lon, lat, alt, lon, lat, alt],
                    ),
                    properties={
                        "datetime": t.utc_datetime(),
                        "start": t.utc_datetime() - self._model.block_time[0],
                        "end": t.utc_datetime() + self._model.block_time[1],
                        "view:off_nadir": off_nadir,
                        "view:azimuth": (azimuth.degrees + 180) % 360,
                        "view:elevation": elevation.degrees,
                        "sun:elevation": 0,
                        "sun:azimuth": 0,
                    },
                )
            )

        return passes

    def off_nadir(self, t: datetime | Time, lon: float, lat: float, alt=0.0) -> float:
        if isinstance(t, datetime):
            ts = load.timescale()
            t = ts.from_datetime(t)

        target = wgs84.latlon(lat, lon, alt)
        sat_ecef = self.at(t).frame_xyz(itrs).m
        vec_ecef = (self - target).at(t).frame_xyz(itrs).m

        return np.degrees(
            np.arccos(
                np.clip(
                    np.dot(
                        _unit_vector(vec_ecef),
                        _unit_vector(sat_ecef),
                    ),
                    -1.0,
                    1.0,
                )
            )
        )
