"""Cross-platform file locking.

On Unix, uses fcntl.flock(). On Windows, uses msvcrt.locking() with a small
wrapper that emulates flock() behavior (blocking vs non-blocking, shared vs
exclusive distinction is best-effort).

Usage:
    from arcade.filelock import flock, LOCK_EX, LOCK_NB, LOCK_UN

    with open('lockfile', 'a+') as f:
        flock(f, LOCK_EX)  # blocking exclusive lock
        # ... critical section ...
        flock(f, LOCK_UN)  # unlock
"""
from __future__ import annotations

import os
import sys
import time

LOCK_SH = 1  # shared lock
LOCK_EX = 2  # exclusive lock
LOCK_NB = 4  # non-blocking
LOCK_UN = 8  # unlock

if sys.platform == "win32":
    import msvcrt

    def flock(f, op: int) -> None:
        """Emulate Unix flock() using msvcrt.locking() on Windows.

        msvcrt.locking() works on byte ranges, not the whole file, so we lock
        just the first byte. This is sufficient for advisory locking as used
        by the supervisor and xchain payout lock.
        """
        fd = f if isinstance(f, int) else f.fileno()
        try:
            os.lseek(fd, 0, 0)
        except OSError:
            pass

        if op & LOCK_UN:
            try:
                msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
            except OSError:
                pass
            return

        while True:
            try:
                msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
                return
            except OSError:
                if op & LOCK_NB:
                    raise BlockingIOError("file is locked")
                time.sleep(0.2)

else:
    import fcntl as _fcntl

    LOCK_SH = _fcntl.LOCK_SH
    LOCK_EX = _fcntl.LOCK_EX
    LOCK_NB = _fcntl.LOCK_NB
    LOCK_UN = _fcntl.LOCK_UN

    def flock(f, op: int) -> None:
        """Use the native fcntl.flock() on Unix."""
        _fcntl.flock(f, op)
