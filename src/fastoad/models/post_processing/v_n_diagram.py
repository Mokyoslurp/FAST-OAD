"""Computation of the V-n diagram."""
#  This file is part of FAST-OAD : A framework for rapid Overall Aircraft Design
#  Copyright (C) 2021 ONERA & ISAE-SUPAERO
#  FAST is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURpositiveE.  See the
#  GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

import numpy as np
import openmdao.api as om
from stdatm import Atmosphere
from fastoad.module_management._plugins import FastoadLoader

FastoadLoader()


class VnDiagram(om.ExplicitComponent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._engine_wrapper = None

    def initialize(self):

        self.options.declare("propulsion_id", default="", types=str)

    def setup(self):

        self.add_input("data:geometry:wing:area", units="m**2", val=np.nan)
        self.add_input("data:geometry:wing:MAC:length", units="m", val=np.nan)
        self.add_input("data:weight:aircraft:MTOW", units="kg", val=np.nan)
        self.add_input("data:weight:aircraft:MZFW", units="kg", val=np.nan)
        self.add_input("data:aerodynamics:aircraft:cruise:CL", val=np.nan, shape=150)
        self.add_input("data:aerodynamics:aircraft:cruise:CL_alpha", val=np.nan)
        self.add_input("data:TLAR:cruise_mach", val=np.nan)

        self.add_output(
            "data:performance:V-n_diagram:v_stall",
            units="m/s",
        )
        self.add_output(
            "data:performance:V-n_diagram:MTOW:v_manoeuvre",
            units="m/s",
        )
        self.add_output(
            "data:performance:V-n_diagram:MTOW:v_manoeuvre_negative",
            units="m/s",
        )
        self.add_output(
            "data:performance:V-n_diagram:MZFW:v_manoeuvre",
            units="m/s",
        )
        self.add_output(
            "data:performance:V-n_diagram:MZFW:v_manoeuvre_negative",
            units="m/s",
        )
        self.add_output(
            "data:performance:V-n_diagram:v_cruising",
            units="m/s",
        )
        self.add_output(
            "data:performance:V-n_diagram:v_dive",
            units="m/s",
        )
        self.add_output(
            "data:performance:V-n_diagram:MTOW:n_v_c_positive",
            units="m/s",
        )
        self.add_output(
            "data:performance:V-n_diagram:MTOW:n_v_c_negative",
            units="m/s",
        )
        self.add_output(
            "data:performance:V-n_diagram:MTOW:n_v_d_positive",
            units="m/s",
        )
        self.add_output(
            "data:performance:V-n_diagram:MTOW:n_v_d_negative",
            units="m/s",
        )
        self.add_output(
            "data:performance:V-n_diagram:MZFW:n_v_c_positive",
            units="m/s",
        )
        self.add_output(
            "data:performance:V-n_diagram:MZFW:n_v_c_negative",
            units="m/s",
        )
        self.add_output(
            "data:performance:V-n_diagram:MZFW:n_v_d_positive",
            units="m/s",
        )
        self.add_output(
            "data:performance:V-n_diagram:MZFW:n_v_d_negative",
            units="m/s",
        )
        self.add_output(
            "data:performance:V-n_diagram:v_1g_negative",
            units="m/s",
        )

    def compute(self, inputs, outputs, discrete_inputs=None, discrete_outputs=None):

        wing_area = float(inputs["data:geometry:wing:area"])
        mtow = float(inputs["data:weight:aircraft:MTOW"])
        mzfw = float(inputs["data:weight:aircraft:MZFW"])
        cl_vector_input = inputs["data:aerodynamics:aircraft:cruise:CL"]
        mac = float(inputs["data:geometry:wing:MAC:length"])  # length of the mean aerodynamic chord
        cl_alpha = float(inputs["data:aerodynamics:aircraft:cruise:CL_alpha"])
        cruise_mach = inputs["data:TLAR:cruise_mach"][0]

        g = 9.80665  # m/s^2
        atm = Atmosphere(altitude=20000, altitude_in_feet=True)
        rho = atm.density

        maximum_positive_load_factor_mtow = 2.1 + 24000 / (10000 + mtow * 2.2046)  # n_max for mtow
        if maximum_positive_load_factor_mtow < 2.5:
            maximum_positive_load_factor_mtow = 2.5
        elif maximum_positive_load_factor_mtow > 3.8:
            maximum_positive_load_factor_mtow = 3.8
        maximum_negative_load_factor_mtow = -0.4 * maximum_positive_load_factor_mtow

        maximum_positive_load_factor_mzfw = 2.1 + 24000 / (10000 + mzfw * 2.2046)  # n_max for mzfw
        if maximum_positive_load_factor_mzfw < 2.5:
            maximum_positive_load_factor_mzfw = 2.5
        elif maximum_positive_load_factor_mzfw > 3.8:
            maximum_positive_load_factor_mzfw = 3.8
        maximum_negative_load_factor_mzfw = -0.4 * maximum_positive_load_factor_mzfw

        cl_max = max(cl_vector_input)
        cn_max = 1.1 * cl_max
        cn_min = -1.3

        v_stall_equivalent = np.sqrt(
            2 * mtow * g / (1.225 * wing_area * cn_max)
        )  # stall speed of the aircraft and also the speed at which the load factor is equal to 1
        v_1g_negative = np.sqrt(
            2 * mtow * g / (1.225 * wing_area * np.abs(cn_min))
        )  # speed at which the load factor is equal to -1

        v_manoeuvre_equivalent_mtow = np.sqrt(
            (2 * mtow * g * maximum_positive_load_factor_mtow) / (1.225 * wing_area * cn_max)
        )  # manoeuvre speed at maximum positive load factor
        if v_manoeuvre_equivalent_mtow < v_stall_equivalent * np.sqrt(
            maximum_positive_load_factor_mtow
        ):
            v_manoeuvre_equivalent_mtow = v_stall_equivalent * np.sqrt(
                maximum_positive_load_factor_mtow
            )

        v_manoeuvre_equivalent_mzfw = np.sqrt(
            (2 * mzfw * g * maximum_positive_load_factor_mzfw) / (1.225 * wing_area * cn_max)
        )  # manoeuvre speed at maximum positive load factor
        if v_manoeuvre_equivalent_mzfw < v_stall_equivalent * np.sqrt(
            maximum_positive_load_factor_mzfw * mzfw / mtow
        ):
            v_manoeuvre_equivalent_mzfw = v_stall_equivalent * np.sqrt(
                maximum_positive_load_factor_mzfw * mzfw / mtow
            )

        v_manoeuvre_equivalent_negative_mtow = np.sqrt(
            (2 * mtow * g * np.abs(maximum_negative_load_factor_mtow))
            / (1.225 * wing_area * np.abs(cn_min))
        )  # manoeuvre speed at maximum negative load factor
        v_manoeuvre_equivalent_negative_mzfw = np.sqrt(
            (2 * mzfw * g * np.abs(maximum_negative_load_factor_mzfw))
            / (1.225 * wing_area * np.abs(cn_min))
        )  # manoeuvre speed at maximum negative load factor

        v_cruising_equivalent = (
            cruise_mach * atm.speed_of_sound * np.sqrt(rho / 1.225)
        )  # speed does not vary between MZFW and MTOW
        v_dive_equivalent = ((0.07 + cruise_mach) * atm.speed_of_sound) * np.sqrt(
            rho / 1.225
        )  # speed does not vary between MZFW and MTOW

        if v_dive_equivalent < 1.25 * v_cruising_equivalent:
            v_dive_equivalent = 1.25 * v_cruising_equivalent

        u_gust_v_c = 50.0 * 0.3048  # 50ft/s into m/s
        u_gust_v_d = 25.0 * 0.3048  # 50ft/s into m/s

        # Computation for MTOW
        mu = 2 * mtow / (rho * wing_area * mac * cl_alpha)
        K_g = (0.88 * mu) / (5.3 + mu)

        n_v_c_positive = 1 + (
            (1.225 * K_g * u_gust_v_c * v_cruising_equivalent * wing_area * cl_alpha)
            / (2 * g * mtow)
        )  # load factor at cruising speed for a gust of 50 ft/s

        n_v_d_positive = 1 + (
            (1.225 * K_g * u_gust_v_d * v_dive_equivalent * wing_area * cl_alpha) / (2 * g * mtow)
        )  # load factor at diving speed for a gust of 25 ft/s

        n_v_c_negative = 1 - (
            (1.225 * K_g * u_gust_v_c * v_cruising_equivalent * wing_area * cl_alpha)
            / (2 * g * mtow)
        )  # load factor at cruising speed for a gust of -50 ft/s
        n_v_d_negative = 1 - (
            (1.225 * K_g * u_gust_v_d * v_dive_equivalent * wing_area * cl_alpha) / (2 * g * mtow)
        )  # load factor at cruising speed for a gust of -25 ft/s

        outputs["data:performance:V-n_diagram:MTOW:n_v_c_positive"] = n_v_c_positive
        outputs["data:performance:V-n_diagram:MTOW:n_v_c_negative"] = n_v_c_negative
        outputs["data:performance:V-n_diagram:MTOW:n_v_d_positive"] = n_v_d_positive
        outputs["data:performance:V-n_diagram:MTOW:n_v_d_negative"] = n_v_d_negative
        outputs["data:performance:V-n_diagram:MTOW:v_manoeuvre"] = v_manoeuvre_equivalent_mtow
        outputs[
            "data:performance:V-n_diagram:MTOW:v_manoeuvre_negative"
        ] = v_manoeuvre_equivalent_negative_mtow

        # Computation for MZFW
        mu = 2 * mzfw / (rho * wing_area * mac * cl_alpha)
        K_g = (0.88 * mu) / (5.3 + mu)

        n_v_c_positive = 1 + (
            (1.225 * K_g * u_gust_v_c * v_cruising_equivalent * wing_area * cl_alpha)
            / (2 * g * mzfw)
        )  # load factor at cruising speed for a gust of 50 ft/s
        n_v_d_positive = 1 + (
            (1.225 * K_g * u_gust_v_d * v_dive_equivalent * wing_area * cl_alpha) / (2 * g * mzfw)
        )  # load factor at cruising speed for a gust of 25 ft/s

        n_v_c_negative = 1 - (
            (1.225 * K_g * u_gust_v_c * v_cruising_equivalent * wing_area * cl_alpha)
            / (2 * g * mzfw)
        )  # load factor at cruising speed for a gust of -50 ft/s
        n_v_d_negative = 1 - (
            (1.225 * K_g * u_gust_v_d * v_dive_equivalent * wing_area * cl_alpha) / (2 * g * mzfw)
        )  # load factor at cruising speed for a gust of -25 ft/s

        outputs["data:performance:V-n_diagram:MZFW:n_v_c_positive"] = n_v_c_positive
        outputs["data:performance:V-n_diagram:MZFW:n_v_c_negative"] = n_v_c_negative
        outputs["data:performance:V-n_diagram:MZFW:n_v_d_positive"] = n_v_d_positive
        outputs["data:performance:V-n_diagram:MZFW:n_v_d_negative"] = n_v_d_negative
        outputs["data:performance:V-n_diagram:MZFW:v_manoeuvre"] = v_manoeuvre_equivalent_mzfw
        outputs[
            "data:performance:V-n_diagram:MZFW:v_manoeuvre_negative"
        ] = v_manoeuvre_equivalent_negative_mzfw

        # Put the resultst in the output file
        outputs["data:performance:V-n_diagram:v_stall"] = v_stall_equivalent
        outputs["data:performance:V-n_diagram:v_1g_negative"] = v_1g_negative
        outputs["data:performance:V-n_diagram:v_cruising"] = v_cruising_equivalent
        outputs["data:performance:V-n_diagram:v_dive"] = v_dive_equivalent
