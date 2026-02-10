#!/usr/bin/env python3
"""Wait for database to be ready"""
import sys
import time

import psycopg


def wait_for_db(max_attempts: int = 30, delay: int = 2) -> int:
    """Wait for database to accept connections"""
    db_url = "postgresql://lab:lab@postgres:5432/lab"

    for attempt in range(1, max_attempts + 1):
        try:
            conn = psycopg.connect(db_url, connect_timeout=5)
            conn.close()
            print(f"✓ Database ready after {attempt} attempt(s)")
            return 0
        except psycopg.Error as e:
            if attempt == max_attempts:
                print(f"✗ Database not ready after {max_attempts} attempts")
                print(f"Last error: {e}")
                return 1

            print(f"Attempt {attempt}/{max_attempts}: Database not ready, waiting...")
            time.sleep(delay)

    return 1


if __name__ == "__main__":
    sys.exit(wait_for_db())
