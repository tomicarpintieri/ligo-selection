"""Which directions a detector can hear, and how that changes as the Earth turns.

STATUS: skeleton. Filled in by TASKS/day-4-antenna.md (detector frame) and
TASKS/day-5-network.md (real detectors, sidereal time, the network).

This is the part day 2 of the course explicitly left out: "No antenna patterns.
No sky localisation. We do not do a coherent multi-detector search -- for
simplicity. Every number today is computed from a single interferometer."
Everything in this module is therefore new relative to the course.

An L-shaped detector measures the difference in length between two perpendicular
arms. A wave arriving in the right orientation stretches one arm and squeezes
the other: maximum signal. Arriving rotated by 45 degrees it stretches both
equally, the difference is zero, and the detector sees nothing at all. There are
four such directions, and they are geometry, not a defect.
"""
import numpy as np


def response(theta, phi, psi):
    """F_plus and F_cross in the DETECTOR frame. No Earth, no time.

    theta from the zenith (normal to the plane of the arms), phi from the x arm,
    psi the polarisation angle. All radians; all broadcast over arrays.

    MUST SATISFY -- these were measured on this machine with N = 4e6, seed 0,
    before any of this was written:
      F_plus(0, 0, 0) = 1            and F_cross(0, 0, 0) = 0     to 1e-12
      F_plus = F_cross = 0           at theta = pi/2 and
                                     phi in {pi/4, 3pi/4, 5pi/4, 7pi/4},
                                     for EVERY psi, to 1e-12
      <F_plus^2>  over sky and psi  = 1/5  (measured 0.19997)
      <F_cross^2> over sky and psi  = 1/5  (measured 0.19987)
      <F_plus F_cross>              = 0    (measured -3.6e-05)

    The sky average is the sharp test. Sample cos(theta) uniformly, not theta:
    the classic error gives a smooth wrong answer with no symptom, and
    tests/test_04_antenna.py::test_bad_sky_sampler_fails exists to prove the
    check can tell the difference.
    """
    raise NotImplementedError("TASKS/day-4-antenna.md")


def projection_factor(f_plus, f_cross, inclination):
    """How much of an optimally-oriented signal actually reaches the detector.

        w = sqrt( F_plus^2 ((1 + cos^2 i)/2)^2 + F_cross^2 cos^2 i )

    w = 1 is the best possible source: overhead, face-on. The observed SNR is
    w times the sigma of the same source at the same distance.

    MUST SATISFY, averaging over sky, polarisation and inclination:
      <w^2>^(1/2)     = 2/5      -> 1/x = 2.5000   (measured 2.5003)
      <w^3>^(-1/3)    = 2.2649                     (measured 2.2649)

    The second is the number this project exists to start with: the ratio
    between the horizon distance (best case) and the range (volume-equivalent
    average). Day 2 of the course mentions "the averaged range is 2.26x smaller"
    in a presenter note and never computes it.
    """
    raise NotImplementedError("TASKS/day-4-antenna.md")


# ---------------------------------------------------------------- day 5
# Below here the detector gets bolted to the Earth and the Earth starts turning.

def gmst_from_gps(gps):
    """Greenwich Mean Sidereal Time, in radians, from a GPS second.

    Written from scratch and checked against astropy.time, which is a test-only
    dependency -- that comparison is the provenance entry, not the implementation.

    MUST SATISFY:
      gmst(t + 86164.0905 s) - gmst(t) = 2 pi   to 1e-6 rad
      agrees with astropy.time                  to 1e-4 rad
    """
    raise NotImplementedError("TASKS/day-5-network.md")


def response_earth(detector, ra, dec, psi, gps):
    """F_plus and F_cross for a real detector, a sky position, and a moment.

    Right ascension and declination are fixed to the stars; the detector is
    fixed to the Earth; gmst_from_gps is what connects them. Which means the
    answer for a fixed source changes over 24 hours, and a source that was in a
    blind spot at 3 a.m. is audible by nine.

    MUST SATISFY: <F_plus^2> over the sky is still 1/5 at any gps -- a rotation
    cannot change an average over all directions.
    """
    raise NotImplementedError("TASKS/day-5-network.md")


def time_delay(det_a, det_b, ra, dec, gps):
    """Arrival-time difference between two detectors, in seconds.

    MUST SATISFY:
      |delay(H1, L1)| <= 10.002 ms for every sky direction -- the light travel
        time between the two sites, which is a property of the geometry alone
      the observed GW150914 offset of -7.08 ms picks out a non-empty ring of sky
        directions. That is a CONSISTENCY check and not a precision one: the
        published localisation is a banana of about 600 square degrees, and the
        page has to say so in those words.
    """
    raise NotImplementedError("TASKS/day-5-network.md")
