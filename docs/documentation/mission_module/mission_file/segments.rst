.. _flight-segments:


###############
Flight segments
###############

Flight segments are the Python-implemented, base building blocks for the mission definition.

They can be used as parts in :ref:`phase <phase-section>` definition.

A segment simulation starts at the flight parameters (altitude, speed, mass...) reached at
the end of the previous simulated segment.
The segment simulation ends when its **target** is reached (or if it cannot be reached).

Sections:

.. contents::
   :local:
   :depth: 1


*************
Segment types
*************

In the following, the description of each segment type links to the documentation of the
Python implementation.
All parameters of the Python constructor can be set in the mission file (except for
:code:`propulsion` and :code:`reference_area` that are set within the mission module).
Most of these parameters are scalars and can be set as described :ref:`here<setting-values>`.
The segment target is a special parameter, detailed in :ref:`further section<segment-target>`
Special parameters are detailed in :ref:`last section<segment-special-parameters>`.



Available segments are:

.. contents::
   :local:
   :depth: 1

.. _segment-speed_change:


:code:`speed_change` segment
============================

A :code:`speed_change` segment simulates an acceleration or deceleration flight part, at constant
altitude and thrust rate. It ends when the target speed (mach, true_airspeed or
equivalent_airspeed) is reached.

Python documentation: :mod:`~fastoad.models.performances.mission.segments.speed_change.SpeedChangeSegment`

**Example:**

.. code-block:: yaml

    segment: speed_change
    polar: data:aerodynamics:aircraft:takeoff   # High-lift devices are ON
    engine_setting: takeoff
    thrust_rate: 1.0                            # Full throttle
    target:
      # altitude: constant                      # Assumed by default
      equivalent_airspeed:                      # Acceleration up to EAS = 250 knots
        value: 250
        unit: kn


.. _segment-altitude_change:

:code:`altitude_change` segment
===============================

An :code:`altitude_change` segment simulates a climb or descent flight part at constant thrust rate.
Typically, it ends when the target altitude is reached.

But also, a target speed can be set, while keeping another speed constant (e.g. climbing up to
Mach 0.8 while keeping equivalent_airspeed constant).

Python documentation: :class:`~fastoad.models.performances.mission.segments.altitude_change.AltitudeChangeSegment`

**Examples:**

.. code-block:: yaml

    segment: altitude_change
    polar: data:aerodynamics:aircraft:cruise    # High speed aerodynamic polar
    engine_setting: idle
    thrust_rate: 0.15                           # Idle throttle
    target:                                     # Descent down to 10000. feet at constant EAS
      altitude:
        value: 10000.
        unit: ft
      equivalent_airspeed: constant


.. code-block:: yaml

    segment: altitude_change
    polar: data:aerodynamics:aircraft:cruise    # High speed aerodynamic polar
    engine_setting: climb
    thrust_rate: 0.93                           # Climb throttle
    target:                                     # Climb up to Mach 0.78 at constant EAS
      equivalent_airspeed: constant
      mach: 0.78

.. code-block:: yaml

    segment: altitude_change
    polar: data:aerodynamics:aircraft:cruise    # High speed aerodynamic polar
    engine_setting: climb
    thrust_rate: 0.93                           # Climb throttle
    target:                                     # Climb at constant Mach up to the flight
      mach: constant                            #  level that provides maximum lift/drag
      altitude:                                 #  at current mass.
        value: optimal_flight_level


.. _segment-cruise:

:code:`cruise` segment
======================

A :code:`cruise` segment simulates a flight part at constant speed and altitude, and regulated
thrust rate (drag is compensated).

Optionally, target altitude can be set to :code:`optimal_flight_level`. In such case, cruise will
be preceded by a climb segment that will put the aircraft at the altitude that will minimize the
fuel consumption for the whole segment (including the prepending climb).
This option is available because the :ref:`segment-altitude_change` segment can reach an altitude
that will optimize the lift/drag ratio at current mass, but the obtained altitude will not
guaranty an optimal fuel consumption for the whole cruise.

It ends when the target ground distance is covered (including the distance covered during
prepending climb, if any).

Python documentation: :class:`~fastoad.models.performances.mission.segments.cruise.ClimbAndCruiseSegment`

**Examples:**

.. code-block:: yaml

    segment: cruise
    polar: data:aerodynamics:aircraft:cruise    # High speed aerodynamic polar
    engine_setting: cruise
    target:
      # altitude: constant                      # Not needed, because assumed by default
      ground_distance:                          # Cruise for 2000 nautical miles
        value: 2000
        unit: NM

.. code-block:: yaml

    segment: cruise
    polar: data:aerodynamics:aircraft:cruise    # High speed aerodynamic polar
    engine_setting: cruise
    target:
      altitude: optimal_flight_level            # Commands a prepending climb, id needed
      ground_distance:                          # Cruise for 2000 nautical miles
        value: 2000
        unit: NM

.. _segment-optimal_cruise:

:code:`optimal_cruise` segment
==============================

An :code:`optimal_cruise` segment simulates a cruise climb, i.e. a cruise where the aircraft
climbs gradually to keep being at altitude of maximum lift/drag ratio.

It assumed the segment actually starts at altitude of maximum lift/drag ratio, which can be
achieved with an :ref:`segment-altitude_change` segment with :code:`optimal_altitude` as target
altitude.

*The common way to optimize the fuel consumption for commercial aircraft is a step climb cruise.
Such segment will be implemented in the future.*

Python documentation: :class:`~fastoad.models.performances.mission.segments.cruise.OptimalCruiseSegment`

**Example:**

.. code-block:: yaml

    segment: optimal_cruise
    polar: data:aerodynamics:aircraft:cruise    # High speed aerodynamic polar
    engine_setting: cruise
    target:
      ground_distance:                          # Cruise for 2000 nautical miles
        value: 2000
        unit: NM


:code:`holding` segment
=======================

A :code:`holding` segment simulates a flight part at constant speed and altitude, and regulated
thrust rate (drag is compensated). It ends when
the target time is covered.

Python documentation: :class:`~fastoad.models.performances.mission.segments.hold.HoldSegment`

**Example:**

.. code-block:: yaml

    segment: holding
    polar: data:aerodynamics:aircraft:cruise    # High speed aerodynamic polar
    target:
      # altitude: constant                      # Not needed, because assumed by default
      time:
        value: 20                               # 20 minutes holding
        unit: min


:code:`taxi` segment
====================

A :code:`taxi` segment simulates the mission parts between gate and takeoff or landing, at constant
thrust rate. It ends when the target time is covered.

Python documentation: :class:`~fastoad.models.performances.mission.segments.taxi.TaxiSegment`

**Example:**

.. code-block:: yaml

    segment: taxi
    thrust_rate: 0.3
    target:
      time:
        value: 300              # taxi for 300 seconds (5 minutes)

:code:`transition` segment
==========================

A :code:`transition` segment is intended to "fill the gaps" when some flight part is not available
for computation or is needed to be assessed without spending CPU time.

It can be used in various ways:

.. contents::
   :local:
   :depth: 1

Target definition
-----------------
The most simple way is specifying a target with absolute and/or relative parameters. The second and
last point of the flight segment will simply uses these values.

**Example:**

.. code-block:: yaml

    segment: transition # Rough simulation of a takeoff
    target:
      delta_time: 60            # 60 seconds after start point
      delta_altitude:           # 35 ft above start point
        value: 35
        unit: ft
      delta_mass: -80.0         # 80kg lost from start point
      true_airspeed: 85         # 85m/s at end of segment.

Usage of a mass ratio
---------------------

As seen above, it is possible to force a mass evolution of a certain amount by specifying
:code:`delta_mass`.

It is also possible to specify a mass ratio. This can be done outside the target, as a segment
parameter.

**Example:**

    segment: transition # Rough climb simulation
    mass_ratio: 0.97            # Aircraft end mass will be 97% of total start mass
    target:
      altitude: 10000.
      mach: 0.78
      delta_ground_distance:    # 250 km after start point.
        value: 250
        unit: km

Reserve mass ratio
------------------

Another segment parameter is :code:`reserve_mass_ratio`. When using this parameter, another flight
point is added to computed segment, where the aircraft mass is decreased by a fraction of the mass
that remains at the end of the segment (including this reserve consumption).

Typically, it will be used as last segment to compute a reserve based on the Zero-Fuel-Weight mass.

**Example:**

    segment: transition # Rough reserve simulation
    reserve_mass_ratio: 0.06
    target:
      altitude: 0.
      mach: 0.



.. _segment-target:

**************
Segment target
**************

The target of a flight segment is a set of parameters that drives the end of the segment simulation.

Possible target parameters are the available fields of
:class:`~fastoad.model_base.flight_point.FlightPoint`. The actually useful parameters depend on the
segment.

Each parameter can be set the :ref:`usual way<setting-values>`, generally with a numeric value or
a variable name, but it can also be a string. The most common string value is :code:`constant`
that tells the parameter value should be kept constant and equal to the start value.
In any case, please refer to the documentation of the flight segment.

Absolute and relative values
============================

Amost all target parameters are considered as absolute values, i.e. the target is considered
reached if the named parameter gets equal to the provided value.

They can also be specified as relative values, meaning that the target is considered reached if the
named parameter gets equal to the provided value **added** to start value. To do so, the parameter
name will be preceded by :code:`delta_`.

**Examples:**

.. code-block:: yaml

    target:
      altitude: # Target will be reached at 35000 ft.
        value: 35000
        unit: ft

.. code-block:: yaml

    target:
      delta_altitude: # Target will be 5000 ft above the start altitude of the segment.
        value: 5000
        unit: ft

.. important::
    There are 2 exceptions : :code:`ground_distance` and :code:`time` are always considered as
    relative values. Therefore, :code:`delta_ground_distance` and :code:`delta_time` will have the
    same effect.



.. _segment-special-parameters:

**************************
Special segment parameters
**************************

Most of segment parameters must be set with a unique value, which can be done in several ways,
as described :ref:`here<setting-values>`.

There are some special parameters that are detailed below.

.. contents::
   :local:
   :depth: 1



.. _segment-parameter-engine_setting:

:code:`engine_setting` parameter
================================

Expected value for :code:`engine_setting` are :code:`takeoff`, :code:`climb`
, :code:`cruise` or :code:`idle`

This setting is used by the "rubber engine" propulsion model
(see :class:`~fastoad.models.propulsion.fuel_propulsion.rubber_engine.rubber_engine.RubberEngine`).
It roughly links the "turbine inlet temperature" (a.k.a. T4) to the flight conditions.

If another propulsion model is used, this parameter may become irrelevant, and then can be omitted.


.. _segment-parameter-polar:

:code:`polar` parameter(s)
==========================

The aerodynamic polar defines the relation between lift and drag coefficients
(respectively CL and CD).
This parameter is composed of two vectors of same size, one for CL, and one for CD.

The :code:`polar` parameter has 2 sub-keys that are :code:`CL` and :code:`CD`.

A basic example would be:

.. code-block:: yaml

    segment: cruise
    polar:
      CL: [0.0, 0.5, 1.0]
      CD: [0.01, 0.03, 0.12]

But generally, polar values will be obtained through variable names, because they
will be computed during the process, or provided in the input file. This should give:

.. code-block:: yaml

    segment: cruise
    polar:
      CL: data:aerodynamics:aircraft:cruise:CL
      CD: data:aerodynamics:aircraft:cruise:CD

Additionally, a convenience feature is proposes, which assumes CL and CD are provided
by variables with same names, except one ends with :code:`:CL` and the other one by :code:`:CD`.
In such case, providing only the common prefix is enough.

Therefore, the next example is equivalent to the previous one:

.. code-block:: yaml

    segment: cruise
    polar: data:aerodynamics:aircraft:cruise
