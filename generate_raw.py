from __future__ import annotations

import json
import random
from pathlib import Path

import numpy as np
import pandas as pd


RNG_SEED = 20260703
LOTS = ["A", "B", "C", "D"]

ISSUES = {
    "positive_coliform": (34, ["positive coliform screen", "microbial indicator hit", "total-coliform notice"]),
    "ecoli_presumptive": (48, ["presumptive E. coli result", "fecal indicator alert", "E. coli confirmation pending"]),
    "low_chlorine": (24, ["low free-chlorine residual", "chlorine residual below action floor", "residual decay warning"]),
    "pressure_loss": (30, ["pressure loss report", "negative-pressure episode", "unplanned depressurization"]),
    "main_break_near_sewer": (38, ["main break near sewer crossing", "excavation with wastewater proximity", "wet trench near sanitary lateral"]),
    "cross_connection": (44, ["possible cross-connection", "backflow-prevention concern", "unknown hose connection"]),
    "turbidity_spike": (20, ["turbidity spike", "cloudy-water cluster", "elevated nephelometric reading"]),
    "lead_service_line": (19, ["lead-service-line disturbance", "lead-risk premise note", "galvanized-line disturbance"]),
    "taste_odor_cluster": (12, ["taste and odor complaint cluster", "earthy odor calls", "customer odor pattern"]),
    "sensor_fault": (5, ["telemetry-only sensor fault", "SCADA channel disagreement", "instrument drift notice"]),
}

FACILITIES = {
    "hospital": (18, ["hospital service branch", "acute-care campus", "emergency department loop"]),
    "dialysis": (17, ["dialysis clinic service", "renal-care point of use", "dialysis feed branch"]),
    "care_home": (15, ["long-term-care wing", "assisted-living service", "care-home riser"]),
    "school": (10, ["school kitchen wing", "student building service", "campus cafeteria line"]),
    "food_service": (8, ["food-prep tenant", "commercial kitchen block", "licensed food service"]),
    "apartment": (6, ["multi-unit apartment stack", "high-occupancy riser", "residential tower branch"]),
    "industrial": (3, ["industrial customer spur", "warehouse service lateral", "process-water tenant"]),
    "ordinary": (0, ["ordinary residential service", "single customer line", "non-sensitive service"]),
}

EVIDENCE = {
    "lab_confirmed": (15, ["lab-confirmed result", "certified lab report", "chain-of-custody lab hit"]),
    "field_meter": (9, ["field-meter reading", "operator handheld reading", "calibrated field kit"]),
    "customer_cluster": (7, ["clustered customer calls", "multiple premise complaints", "call cluster"]),
    "operator_log": (6, ["operator log entry", "crew field note", "shift log annotation"]),
    "contractor_report": (4, ["contractor report", "excavation crew note", "third-party work order"]),
    "scada_only": (2, ["SCADA-only alert", "remote sensor trace", "telemetry channel only"]),
}

SPREAD = {
    "single_premise": (1, ["one premise", "single service", "one address"]),
    "block": (6, ["one block", "short main segment", "block-level cluster"]),
    "neighborhood": (11, ["neighborhood grid", "multi-block pressure pocket", "several streets"]),
    "pressure_zone": (17, ["entire pressure zone", "zone-wide service area", "large district meter zone"]),
}

TIME_STATE = {
    "resolved": (-8, ["field crew says the condition is already resolved", "temporary isolation is complete", "flush completed before packet time"]),
    "active": (12, ["condition is active at packet time", "still open during dispatch review", "not yet isolated"]),
    "overnight": (8, ["overnight exposure window", "condition likely persisted overnight", "unknown overnight duration"]),
    "recurrent": (14, ["third recurrence this week", "recurrent pattern after prior flush", "repeat event on the same branch"]),
    "short": (2, ["short-duration observation", "brief excursion", "single interval event"]),
}

CONFLICT = {
    "none": (0, ["no contradictory evidence is noted", "records are internally consistent", "no clearance result is available"]),
    "clear_repeat": (-11, ["repeat sample cleared the concern", "second field reading returned normal", "confirmatory check was negative"]),
    "chain_gap": (-5, ["sample chain has a time gap", "custody notes are incomplete", "collection time is uncertain"]),
    "duplicate_ticket": (-7, ["may duplicate a neighboring ticket", "possibly a duplicate complaint", "same event may already be logged"]),
    "conflicting_meter": (-6, ["parallel meter disagreed", "backup meter showed a weaker signal", "alternate gauge was normal"]),
}

MITIGATION = {
    "none": (0, ["no mitigation has started", "no field action has begun", "awaiting first response"]),
    "flush_started": (-4, ["unidirectional flushing has started", "flush crew is on site", "hydrant flushing is underway"]),
    "boil_notice_drafted": (5, ["boil-water notice draft is queued", "public notice template has been opened", "advisory draft is pending"]),
    "valved_off": (-9, ["affected segment has been valved off", "isolation valves are closed", "branch has been isolated"]),
    "bottled_water_sent": (-2, ["bottled water is being delivered", "temporary water cache is dispatched", "customer water totes are staged"]),
}

DISTRICTS = [
    "old cast-iron downtown zone",
    "hillside booster district",
    "coastal low-pressure loop",
    "suburban dead-end grid",
    "mixed hospital-commercial corridor",
    "rural storage-tank extension",
]

REPORT_STYLES = [
    "field_log_digest",
    "lab_exception_summary",
    "customer_call_synthesis",
    "after_action_fragment",
    "shift_handoff_note",
]


def choice_item(rng: random.Random, mapping):
    key = rng.choice(list(mapping.keys()))
    score, phrases = mapping[key]
    return key, score, rng.choice(phrases)


def jitter_phrase(rng: random.Random, text: str) -> str:
    prefixes = ["noted as", "described as", "logged as", "summarized as", "flagged as"]
    suffixes = [
        "before supervisor review",
        "in the dispatch packet",
        "with no address-level identifiers",
        "during the current operating shift",
        "after routine anonymization",
    ]
    return f"{rng.choice(prefixes)} {text} {rng.choice(suffixes)}"


def build_incident(rng: random.Random, lot: str, difficulty: str) -> dict:
    issue, issue_score, issue_phrase = choice_item(rng, ISSUES)
    facility, facility_score, facility_phrase = choice_item(rng, FACILITIES)
    evidence, evidence_score, evidence_phrase = choice_item(rng, EVIDENCE)
    spread, spread_score, spread_phrase = choice_item(rng, SPREAD)
    time_state, time_score, time_phrase = choice_item(rng, TIME_STATE)
    conflict, conflict_score, conflict_phrase = choice_item(rng, CONFLICT)
    mitigation, mitigation_score, mitigation_phrase = choice_item(rng, MITIGATION)

    urgency_words = ["routine", "watch", "same-day", "urgent", "public-health"]
    crew_delay = rng.choice([0, 15, 30, 60, 90, 120])
    vulnerable_bonus = rng.choice([0, 0, 1, 2, 3])
    if facility in {"hospital", "dialysis", "care_home"}:
        vulnerable_bonus += 2
    if issue in {"ecoli_presumptive", "cross_connection", "main_break_near_sewer"}:
        vulnerable_bonus += 1

    decoy_penalty = 0
    if difficulty == "hard" and issue in {"taste_odor_cluster", "sensor_fault"} and evidence in {"lab_confirmed", "field_meter"}:
        decoy_penalty += 4
    if difficulty == "hard" and conflict == "none" and mitigation == "none":
        decoy_penalty += rng.choice([0, 2, 3])

    score = (
        issue_score
        + facility_score
        + evidence_score
        + spread_score
        + time_score
        + conflict_score
        + mitigation_score
        + vulnerable_bonus * 3
        - crew_delay / 40.0
        + decoy_penalty
        + rng.uniform(-1.5, 1.5)
    )

    details = [
        jitter_phrase(rng, issue_phrase),
        jitter_phrase(rng, facility_phrase),
        jitter_phrase(rng, evidence_phrase),
        jitter_phrase(rng, spread_phrase),
        jitter_phrase(rng, time_phrase),
        jitter_phrase(rng, conflict_phrase),
        jitter_phrase(rng, mitigation_phrase),
        f"crew ETA bucket is {crew_delay} minutes",
        f"triage word used by the shift board: {rng.choice(urgency_words)}",
    ]
    rng.shuffle(details)
    text = f"Incident {lot}: " + "; ".join(details) + "."

    return {
        "lot": lot,
        "text": text,
        "score": round(score, 4),
        "issue": issue,
        "facility": facility,
        "evidence": evidence,
        "spread": spread,
        "time_state": time_state,
        "conflict": conflict,
        "mitigation": mitigation,
    }


def ranked_manifest(incidents: list[dict]) -> str:
    ranked = sorted(incidents, key=lambda item: item["score"], reverse=True)
    return json.dumps({"ranked_incidents": [item["lot"] for item in ranked]}, separators=(",", ":"))


def make_case(rng: random.Random, idx: int) -> dict:
    difficulty = rng.choices(["easy", "medium", "hard"], weights=[0.22, 0.45, 0.33])[0]
    district = rng.choice(DISTRICTS)
    style = rng.choice(REPORT_STYLES)
    season = rng.choice(["freeze-thaw", "monsoon", "summer demand", "leaf-fall", "construction"])
    incidents = [build_incident(rng, lot, difficulty) for lot in LOTS]

    # Make hard cases less separable by pulling middle scores closer together.
    if difficulty == "hard":
        center = sum(item["score"] for item in incidents) / 4.0
        for item in incidents:
            item["score"] = round(center + 0.68 * (item["score"] - center) + rng.uniform(-0.8, 0.8), 4)

    top = max(incidents, key=lambda item: item["score"])
    evidence_tier = top["evidence"]
    population_band = top["facility"]
    spread_band = top["spread"]

    header = (
        f"Water utility dispatch packet. District context: {district}. "
        f"Report style: {style}. Seasonal context: {season}. "
        "All street names, account numbers, and sample identifiers are removed. "
        "Rank the four incidents for first manual dispatch and public-health escalation."
    )
    body = " ".join(item["text"] for item in incidents)
    footer = (
        "Dispatchers should prioritize acute microbial or pressure-related risk, sensitive users, "
        "wider spread, stronger evidence, active exposure, and unresolved mitigation while accounting "
        "for clear repeat samples, duplicate tickets, or instrument-only artifacts."
    )

    record = {
        "raw_case_id": f"raw_wip_{idx:06d}",
        "district_context": district,
        "report_style": style,
        "incident_count": 4,
        "incident_report": f"{header} {body} {footer}",
        "dispatch_manifest": ranked_manifest(incidents),
        "dominant_hazard": top["issue"],
        "service_context": population_band,
        "evidence_tier": evidence_tier,
        "spread_band": spread_band,
        "difficulty_tier": difficulty,
    }
    for item in incidents:
        record[f"priority_score_{item['lot']}"] = item["score"]
        record[f"issue_{item['lot']}"] = item["issue"]
    return record


def main() -> None:
    rng = random.Random(RNG_SEED)
    rows = [make_case(rng, idx) for idx in range(7600)]
    df = pd.DataFrame(rows)
    out = Path(__file__).resolve().parent / "data.csv"
    df.to_csv(out, index=False)
    print(f"wrote {len(df):,} rows to {out}")


if __name__ == "__main__":
    main()

