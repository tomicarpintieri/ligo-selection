"""Numbers this project does not measure: physical constants and analysis choices.

Anything measured belongs in results.json, not here. Anything here that came
from somewhere is cited on the line that defines it.
"""

# ---------------------------------------------------------------- physics
G = 6.67430e-11            # m^3 kg^-1 s^-2   CODATA 2018
C = 299792458.0            # m s^-1           exact, SI definition
MSUN = 1.98892e30          # kg               the value day 2's reproduce.py used;
                           #                  kept identical so SNRs compare exactly
MPC = 3.0856775814913673e22    # m            IAU 2015 parsec x 1e6

# Solar mass in seconds and metres -- the units most of the waveform algebra is
# cleanest in.  GM/c^3 and GM/c^2.
MSUN_S = G * MSUN / C ** 3
MSUN_M = G * MSUN / C ** 2

# ---------------------------------------------------------------- the data
FS = 4096.0                # Hz, the sample rate of the shipped strain
SEG_S = 32                 # s, the analysis segment length (day 2's choice)
F_LOW = 20.0               # Hz, where the shipped waveforms start
F_HIGH = 1024.0            # Hz, the top of the analysis band

EVENT_GPS = 1126259462.4   # GW150914, published. Used only to say whether we agree.

# ---------------------------------------------------------------- thresholds
RHO_THR = 8.0              # the single-detector SNR a source must beat to count
                           # as detected. The day 2 horizon slide uses 8; Roulet &
                           # Zaldarriaga (2019) use 9. Both appear in the
                           # literature and the choice is recorded per result.

# ---------------------------------------------------------------- reference values
# Published or previously measured numbers we test against. Not inputs to any
# calculation -- targets. Each one names where it comes from.
SIDEREAL_DAY_S = 86164.0905        # s, one rotation of the Earth w.r.t. the stars
H1_L1_LIGHT_TRAVEL_MS = 10.002     # ms, the published H1-L1 separation over c
