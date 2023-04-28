"""Classes for Taxi sequences."""
#  This file is part of FAST-OAD : A framework for rapid Overall Aircraft Design
#  Copyright (C) 2023 ONERA & ISAE-SUPAERO
#  FAST is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

from dataclasses import dataclass, field
from typing import Tuple

import pandas as pd

from fastoad.model_base import FlightPoint
from ..base import RegisterSegment
from ..time_step_base import AbstractFixedDurationSegment, AbstractManualThrustSegment
from ...base import UNITS
from ...polar import Polar


@RegisterSegment("taxi")
@dataclass
class TaxiSegment(AbstractManualThrustSegment, AbstractFixedDurationSegment):
    """
    Class for computing Taxi phases.

    Taxi phase has a target duration (target.time should be provided) and is at
    constant altitude, speed and thrust rate.
    """

    polar: Polar = None
    reference_area: float = field(default=1.0, metadata={UNITS: "m**2"})
    time_step: float = field(default=60.0, metadata={UNITS: "s"})

    #: The imposed speed during taxi. Used for distance computation, and may have an effect on
    #: propulsion.
    true_airspeed: float = field(default=0.0, metadata={UNITS: "m/s"})

    def get_gamma_and_acceleration(self, flight_point: FlightPoint) -> Tuple[float, float]:
        return 0.0, 0.0

    def compute_from_start_to_target(self, start: FlightPoint, target: FlightPoint) -> pd.DataFrame:
        start.mach = None
        start.equivalent_airspeed = None
        start.true_airspeed = self.true_airspeed
        self.complete_flight_point(start)

        return super().compute_from_start_to_target(start, target)
