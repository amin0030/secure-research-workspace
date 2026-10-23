
import os
import secrets
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parents[1]

SERVICES = [
    ("booking_service", 18701),
    ("confirmation_service", 18702),
    ("app_api", 18700),
]


def wait_for_service(process, port):
    url = f"http://127.0.0.1:{port}/openapi.json"
    deadline = time.monotonic() + 30

    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"Service on port {port} stopped unexpectedly")

        try:
            with urlopen(url, timeout=1) as response:
                if response.status == 200:
                    return
        except OSError:
            time.sleep(0.3)

    raise RuntimeError(f"Service on port {port} did not start")


def create_environment(database_path):
    env = os.environ.copy()

    env["APP_TOKEN_SECRET"] = secrets.token_urlsafe(48)
    env["SERVICE_TOKEN_SECRET"] = secrets.token_urlsafe(48)
    env["CONFIRMATION_TOKEN_SECRET"] = secrets.token_urlsafe(48)

    for username in ("AMIN", "CASPER", "FRANK", "RASMUS"):
        env[f"CAMPUS_PASSWORD_{username}"] = secrets.token_urlsafe(24)

    env["BOOKING_DB_PATH"] = str(database_path)
    env["BOOKING_SERVICE_URL"] = "http://127.0.0.1:18701"
    env["CONFIRMATION_SERVICE_URL"] = "http://127.0.0.1:18702"
    env["CAMPUS_TEST_BASE_URL"] = "http://127.0.0.1:18700"

    return env


def main():
    processes = []

    with tempfile.TemporaryDirectory() as directory:
        database_path = Path(directory) / "ci_booking.sqlite3"
        env = create_environment(database_path)

        try:
            for service, port in SERVICES:
                print(f"Starting {service}", flush=True)

                process = subprocess.Popen(
                    [
                        sys.executable,
                        "-m",
                        "uvicorn",
                        "main:app",
                        "--host",
                        "127.0.0.1",
                        "--port",
                        str(port),
                    ],
                    cwd=ROOT / "services" / service,
                    env=env,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.STDOUT,
                )

                processes.append(process)
                wait_for_service(process, port)

            print("All CI services started", flush=True)

            patterns = [
                "test_api_security.py",
                "test_cwe20_timezone.py",
                "test_cwe89_sql_injection.py",
            ]

            for pattern in patterns:
                result = subprocess.run(
                    [
                        sys.executable,
                        "-m",
                        "unittest",
                        "discover",
                        "-s",
                        "tests",
                        "-p",
                        pattern,
                        "-v",
                    ],
                    cwd=ROOT,
                    env=env,
                    check=False,
                )

                if result.returncode != 0:
                    return result.returncode

            print("PASS: All CI integration tests passed", flush=True)
            return 0

        finally:
            for process in reversed(processes):
                if process.poll() is None:
                    process.terminate()

            for process in reversed(processes):
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()

            print("CI services stopped", flush=True)


if __name__ == "__main__":
    sys.exit(main())
