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
from dataclasses import dataclass
from . import constants as k

@dataclass(frozen=True)
class Detector:
    latitude: float
    longitude: float
    elevation: float
    x_arm_azimuth: float

DETECTORS = {
    "H1": Detector(np.deg2rad(46.455), np.deg2rad(-119.408), 142.6, np.deg2rad(125.9994)),
    "L1": Detector(np.deg2rad(30.563), np.deg2rad(-90.774), -6.6, np.deg2rad(197.7165)),
}


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
    theta, phi, psi = np.broadcast_arrays(theta, phi, psi)
    a = 0.5 * (1 + np.cos(theta)**2) * np.cos(2*phi)
    b = np.cos(theta) * np.sin(2*phi)
    return a*np.cos(2*psi) - b*np.sin(2*psi), a*np.sin(2*psi) + b*np.cos(2*psi)


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
    ci = np.cos(inclination)
    return np.sqrt(f_plus**2 * ((1+ci**2)/2)**2 + f_cross**2 * ci**2)


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
    # IAU 1982 expression, GPS converted to Julian date via the Unix epoch.
    jd = np.asarray(gps) / 86400.0 + 2444244.5
    t = (jd - 2451545.0) / 36525.0
    degrees = 280.46061837 + 360.98564736629 * (jd - 2451545.0) + .000387933*t*t - t*t*t/38710000
    return np.deg2rad(np.mod(degrees, 360.0))


def response_earth(detector, ra, dec, psi, gps):
    """F_plus and F_cross for a real detector, a sky position, and a moment.

    Right ascension and declination are fixed to the stars; the detector is
    fixed to the Earth; gmst_from_gps is what connects them. Which means the
    answer for a fixed source changes over 24 hours, and a source that was in a
    blind spot at 3 a.m. is audible by nine.

    MUST SATISFY: <F_plus^2> over the sky is still 1/5 at any gps -- a rotation
    cannot change an average over all directions.
    """
    d = DETECTORS[detector]
    hour = gmst_from_gps(gps) + d.longitude - ra
    theta = np.arccos(np.sin(d.latitude)*np.sin(dec) + np.cos(d.latitude)*np.cos(dec)*np.cos(hour))
    phi = np.arctan2(np.cos(dec)*np.sin(hour), np.cos(d.latitude)*np.sin(dec)-np.sin(d.latitude)*np.cos(dec)*np.cos(hour)) - d.x_arm_azimuth
    return response(theta, phi, psi)


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
    def site(d):
        r = 6371000.0 + d.elevation
        return r*np.array([np.cos(d.latitude)*np.cos(d.longitude), np.cos(d.latitude)*np.sin(d.longitude), np.sin(d.latitude)])
    a, b = DETECTORS[det_a], DETECTORS[det_b]
    n = np.array([np.cos(dec)*np.cos(ra), np.cos(dec)*np.sin(ra), np.sin(dec)])
    return np.dot(site(b)-site(a), n) / k.C
