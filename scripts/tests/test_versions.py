#!/usr/bin/env python3
"""Unit tests for the version predicate engine used by scripts/scan.py."""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("scan", os.path.join(HERE, "..", "scan.py"))
scan = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scan)

CASES = [
    # (installed version, predicate, expected)
    # NOTE: "~1.20-" (a few older Fabric mods) is treated as ">=1.20.0 <1.21.0"
    ("1.20.1", "~1.20-", True),
    ("1.21", "~1.20-", False),
    ("1.20.1", "1.20-1.20.1", True),
    ("1.20.5", "<=1.20.4", False),
    ("2.3.4+1.20.1", ">=2.3.4", True),
    ("1.20.1-2.5.7+refabricated", ">=1.20", True),
    ("1.10.2", ">=1.10.0 <=1.13.0-alpha.4", True),
    ("0.5.13", ">=0.6.0", False),
    ("3.7.2", ">=3.0.0-0", True),
    ("1.20-2.16.38B", ">=1.20-2.5.0", True),
    ("9.2.14+fabric", ">=9.0.8", True),
    ("0.2.0+alpha.11.18", "*", True),
    ("1.0.0+1.20.1", ">=1.0.0", True),
    ("2.13.2+Fabric", "<=2.13.2", True),
    ("2.14.1+Fabric", "<=2.13.2", False),
    ("1.20.1", ">=1.20.1", True),
    ("1.20.1", ">1.20.1", False),
    ("11.1.136+fabric", "^11.0.0", True),
    (">=1.20.1", "*", True),
    ("1.20.1", "~1.20.1", True),
    ("1.20.4", "~1.20.1", True),
    ("1.21.0", "~1.20.1", False),
    ("0.5.9", "^0.5.4", True),
    ("0.6.0", "^0.5.4", False),
]

bad = 0
for version, pred, expected in CASES:
    got = scan.satisfies(version, pred)
    ok = got == expected
    bad += 0 if ok else 1
    print(f"{'OK ' if ok else 'BAD'} {version:26} {pred:26} -> {got} (expected {expected})")
print(f"\n{len(CASES) - bad}/{len(CASES)} passed")
sys.exit(1 if bad else 0)
