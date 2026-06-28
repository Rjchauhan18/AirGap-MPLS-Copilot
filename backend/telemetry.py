"""
Telemetry ingestion layer.

Responsibilities
----------------
- Read telemetry from CSV
- Support future Kafka/Prometheus/gNMI adapters
- Return normalized telemetry dictionaries
"""

from __future__ import annotations

import csv
import time
from pathlib import Path
from typing import Dict, Generator, Optional

from backend.config import TELEMETRY_FILE


class TelemetryReader:
    """
    Reads live telemetry from CSV.

    Future adapters:
        - Kafka
        - Prometheus
        - gNMI
        - SNMP
    """

    def __init__(self, telemetry_file: Optional[Path] = None):

        self.telemetry_file = Path(
            telemetry_file or TELEMETRY_FILE
        )

        if not self.telemetry_file.exists():
            raise FileNotFoundError(
                f"Telemetry file not found: {self.telemetry_file}"
            )

    def tail(self) -> Generator[Dict, None, None]:
        """
        Continuously tails telemetry CSV.

        Returns
        -------
        dict
        """

        with self.telemetry_file.open(
            "r",
            newline=""
        ) as fp:

            reader = csv.DictReader(fp)

            # move to EOF
            fp.seek(0, 2)

            while True:

                line = fp.readline()

                if not line:
                    time.sleep(0.5)
                    continue

                row = line.strip().split(",")

                if len(row) < 10:
                    continue

                try:

                    yield {

                        "timestamp": row[0],

                        "avg_latency_ms": float(row[1]),

                        "jitter_ms": float(row[2]),

                        "packet_loss_pct": float(row[3]),

                        "rx_bytes_per_sec": float(row[4]),

                        "tx_bytes_per_sec": float(row[5]),

                        "bgp_neighbor_state": int(row[6]),

                        "ospf_neighbor_state": int(row[7]),

                        "interface_utilization_pct": float(row[8]),

                        "cpu_utilization_pct": float(row[9]),

                    }

                except Exception:

                    continue