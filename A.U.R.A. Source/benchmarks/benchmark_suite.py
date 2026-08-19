"""
A.U.R.A. Tactical Assistant — Performance Benchmarking Suite.
Measures execution latency, throughput, and algorithmic efficiency across:
1. Hardware Topology Detection & Multi-Device Routing
2. Ship Name & Tactical Dossier Lookup ($O(1)$)
3. Large D-Scan Fleet Parsing & Threat Matrix Categorization
4. Fitting Lab EFT Parsing & Hull Validation
5. Live Intel Log Tailer & Threat Scoring
6. Cold Start & Module Import Overhead
"""
import os
import sys
import time
import psutil

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, app_root)

from hardware import HardwareDetector, DynamicHardwareRouter
from eve_data import lookup_ship, SHIP_DATABASE
from dscan_parser import DScanParser
from fitting_parser import FittingParser
from intel_parser import IntelParser

print("=================================================================")
print("=== A.U.R.A. PERFORMANCE BENCHMARK & ALGORITHM PROFILER ===")
print(f"=== Host CPU: {psutil.cpu_count(logical=False)} Cores / {psutil.cpu_count(logical=True)} Threads ===")
print("=================================================================\n")

# 1. HARDWARE TOPOLOGY SCAN BENCHMARK
t0 = time.perf_counter()
detector = HardwareDetector()
router = DynamicHardwareRouter(detector)
hw_time_ms = (time.perf_counter() - t0) * 1000.0

print(f"1. [Hardware Discovery & Routing]")
print(f"   • Topology: {detector.get_summary_string()}")
print(f"   • Scan Latency: {hw_time_ms:.2f} ms")

t0 = time.perf_counter()
for _ in range(10000):
    router.route_workload(120, turbo_mode=False)
    router.route_workload(500, turbo_mode=True)
route_time_us = ((time.perf_counter() - t0) / 20000.0) * 1000000.0
print(f"   • Workload Routing Latency: {route_time_us:.3f} µs/op ({20000 / (time.perf_counter() - t0):,.0f} ops/sec)\n")


# 2. SHIP DATABASE FUZZY & HASH LOOKUP BENCHMARK
test_queries = [
    "Loki", "cyna", "Vargur", "sabre", "Orthrus", "redeemer", "naglfar",
    "Cerberus", "Kikimora", "barghest", "t3c", "dread", "bo", "cfi",
    "unknown_ship_query", "gate", "bubble", "cyno", "Hound", "Nemesis"
]
num_lookups = 50000
t0 = time.perf_counter()
hits = 0
for i in range(num_lookups):
    q = test_queries[i % len(test_queries)]
    res = lookup_ship(q)
    if res:
        hits += 1
lookup_elapsed = time.perf_counter() - t0
lookup_ops_sec = num_lookups / lookup_elapsed
lookup_avg_us = (lookup_elapsed / num_lookups) * 1000000.0

print(f"2. [Ship Database & Alias Resolution]")
print(f"   • Iterations: {num_lookups:,} queries")
print(f"   • Throughput: {lookup_ops_sec:,.0f} lookups/sec")
print(f"   • Avg Latency: {lookup_avg_us:.3f} µs per lookup (Hit rate: {hits/num_lookups*100:.1f}%)\n")


# 3. D-SCAN 500-ITEM FLEET TABLE PARSING BENCHMARK
sample_dscan_lines = [
    "Sabre\tSabre\t14 km",
    "Loki\tLoki\t28 km",
    "Vargur\tMarauder\t45 km",
    "Cerberus\tHAC\t62 km",
    "Scimitar\tLogistics\t18 km",
    "Orthrus\tCruiser\t85 km",
    "Naglfar\tDreadnought\t120 km",
    "5x Kikimora\tDestroyer\t15 km",
    "Hound\tBomber\t14.3 AU",
    "Revelation\tDreadnought\t100 km"
]
# Generate 500-line fleet scan
massive_dscan = "\n".join(sample_dscan_lines * 50)
dscan_iterations = 200

t0 = time.perf_counter()
total_ships_parsed = 0
for _ in range(dscan_iterations):
    parsed = DScanParser.parse(massive_dscan)
    total_ships_parsed += parsed.get("total_ships", 0)
dscan_elapsed = time.perf_counter() - t0

dscan_throughput_lines = (500 * dscan_iterations) / dscan_elapsed
dscan_avg_ms = (dscan_elapsed / dscan_iterations) * 1000.0

print(f"3. [D-SCAN 500-Ship Fleet Parser & Sorter]")
print(f"   • Fleet Size: 500 vessels / scan (Executed {dscan_iterations} times)")
print(f"   • Processing Time: {dscan_avg_ms:.2f} ms per 500-ship fleet scan")
print(f"   • Parse Throughput: {dscan_throughput_lines:,.0f} D-Scan lines/sec\n")


# 4. FITTING LAB EFT PARSING BENCHMARK
sample_eft_fit = """[Wolf, AM0K-SL TCKL'SAAR'SR Wolf]
Federation Navy 200mm Steel Plates
Gyrostabilizer II
Small Ancillary Armor Repairer
EFFA Compact Assault Damage Control
Coreli A-Type Explosive Coating

Faint Epsilon Scoped Warp Scrambler
5MN Quad LiF Restrained Microwarpdrive

200mm AutoCannon II
200mm AutoCannon II
200mm AutoCannon II
200mm AutoCannon II
Small Ghoul Compact Energy Nosferatu

Small Auxiliary Nano Pump I
Small Projectile Burst Aerator II

Hail S x2480
Republic Fleet Phased Plasma S x2000
Republic Fleet EMP S x2000
Republic Fleet Depleted Uranium S x1000
Barrage S x2000
Republic Fleet Fusion S x2000
Nanite Repair Paste x174
"""

fit_iterations = 2000
t0 = time.perf_counter()
for _ in range(fit_iterations):
    parsed_fit = FittingParser.parse(sample_eft_fit)
fit_elapsed = time.perf_counter() - t0
fit_throughput = fit_iterations / fit_elapsed
fit_avg_us = (fit_elapsed / fit_iterations) * 1000000.0

print(f"4. [Fitting Lab EFT Parser & Slot Classifier]")
print(f"   • Iterations: {fit_iterations:,} EFT fits parsed")
print(f"   • Throughput: {fit_throughput:,.0f} fits/sec")
print(f"   • Avg Latency: {fit_avg_us:.2f} µs per fit\n")


# 5. LIVE INTEL STREAM INGESTION & SPIKE DETECTION BENCHMARK
intel_logs = """[ 19:15:23 ] ScoutPilot > V-3YG7 +5 Loki Cynabal gate bubbled
[ 19:16:01 ] Wingman > 1DQ1-A red dreadnought in local
[ 19:16:45 ] ScoutPilot > Amamake spike 10 hostiles
[ 19:17:12 ] FC > Align gate, cloak up
[ 19:17:30 ] ScoutPilot > Cyno lit! Revelation and Naglfar on beacon
"""
massive_intel = intel_logs * 200 # 1,000 log lines
intel_iterations = 100

t0 = time.perf_counter()
for _ in range(intel_iterations):
    parsed_intel = IntelParser.parse(massive_intel)
intel_elapsed = time.perf_counter() - t0
intel_throughput = (1000 * intel_iterations) / intel_elapsed
intel_avg_ms = (intel_elapsed / intel_iterations) * 1000.0

print(f"5. [Live Intel Log Stream & Threat Detector]")
print(f"   • Ingest Size: 1,000 log lines / batch")
print(f"   • Processing Time: {intel_avg_ms:.2f} ms per 1,000 log lines")
print(f"   • Throughput: {intel_throughput:,.0f} intel lines/sec\n")

print("=================================================================")
print("=== PERFORMANCE BENCHMARK SUITE COMPLETED SUCCESSFULLY ===")
print("=================================================================")
