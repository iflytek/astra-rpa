import argparse
import os
import signal
import sys
import time
from threading import Event

stop_event = Event()


def _install_signal_handlers():
    """Install signal handlers to allow graceful shutdown on Windows and POSIX."""

    def _handler(signum, frame):
        stop_event.set()

    # SIGINT is available on Windows; SIGTERM may not be in some environments
    try:
        signal.signal(signal.SIGINT, _handler)
    except Exception:
        pass
    try:
        signal.signal(signal.SIGTERM, _handler)
    except Exception:
        pass


def main() -> int:
    parser = argparse.ArgumentParser(description="Minimal test app for RPA software integration tests")
    parser.add_argument("args", nargs=argparse.REMAINDER, help="Positional arguments (ignored)")
    parser.add_argument(
        "--sleep",
        type=float,
        default=2.0,
        help="Seconds to sleep before exit when not staying alive",
    )
    parser.add_argument(
        "--stay-alive",
        action="store_true",
        help="If set, keep the process alive until terminated",
    )
    parser.add_argument("--exit-code", type=int, default=0, help="Exit code to return")
    parser.add_argument(
        "--write-pid",
        type=str,
        default="",
        help="If set, write current PID to this file path",
    )

    args = parser.parse_args()

    _install_signal_handlers()

    print(f"test_app started pid={os.getpid()} args={sys.argv[1:]}")
    sys.stdout.flush()

    if args.write_pid:
        try:
            with open(args.write_pid, "w", encoding="utf-8") as f:
                f.write(str(os.getpid()))
        except Exception as e:
            print(f"failed to write pid file: {e}")

    if args.stay_alive:
        # Wait until we receive a signal to stop
        while not stop_event.is_set():
            time.sleep(0.2)
    else:
        # Short-lived mode: give caller time to observe the process
        sleep_seconds = max(0.0, float(args.sleep))
        end_time = time.time() + sleep_seconds
        while time.time() < end_time and not stop_event.is_set():
            time.sleep(0.05)

    print(f"test_app exiting code={args.exit_code}")
    sys.stdout.flush()
    return int(args.exit_code)


if __name__ == "__main__":
    # Make PyInstaller happy on Windows frozen apps
    try:
        from multiprocessing import freeze_support  # type: ignore

        freeze_support()
    except Exception:
        pass
    sys.exit(main())
