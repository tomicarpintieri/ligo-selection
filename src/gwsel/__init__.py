"""gwsel -- what a gravitational-wave detector network can and cannot see.

The package is deliberately flat. Each module owns one idea and none of them
import each other except downwards:

    constants   numbers that are not measured here
    dataio      getting the arrays off disk, and proving they are the right ones
    psd         noise power spectra
    filtering   whitening, and the matched filter
    waveform    the signal, in the frequency domain, with a real amplitude
    horizon     how far a given source can be seen
    antenna     which directions a detector can hear, and when
    figures     one function per figure, sharing one style
    provenance  the record of where every number and figure came from

Nothing here estimates anything it cannot check. Every module's numbers are
pinned by a test in tests/.
"""

__all__ = ["constants", "dataio", "psd", "filtering", "waveform",
           "horizon", "antenna", "figures", "provenance"]
