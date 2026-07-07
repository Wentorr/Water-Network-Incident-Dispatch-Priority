# Water Network Incident Dispatch Priority Dataset

## Overview

This dataset contains anonymized drinking-water utility incident packets. Each row represents one dispatch review packet containing four candidate incidents, labeled A through D, that occurred within the same utility operating window. The goal is to rank the four incidents from highest to lowest response priority using only the public narrative and coarse packet context.

The data was generated locally by the included `generate_raw.py` script with a fixed random seed. The generator creates realistic but privacy-preserving field, laboratory, SCADA, customer-call, and mitigation language inspired by common water-utility operations. No real addresses, customer identifiers, sample identifiers, lab accession numbers, or utility names are included.

## Raw File Structure

The raw dataset upload contains exactly these top-level files:

| File | Description |
|---|---|
| `data.csv` | Raw generated incident packets. Each row contains one four-incident dispatch packet, hidden incident priority scores, the target dispatch manifest, and hidden group columns used only for private grading. |
| `generate_raw.py` | Deterministic Python script that generates `data.csv` from a fixed random seed. It documents the incident vocabularies and scoring ingredients used to create the benchmark. |

The challenge `prepare.py` script, supplied separately in the Eris problem editor, creates `public/train.csv`, `public/test.csv`, `public/sample_submission.csv`, and `private/answers.csv` from `data.csv`.

## Public Prepared Files

| File | Description |
|---|---|
| `train.csv` | 5,000 labeled dispatch packets with public context columns, the incident narrative, and the target `dispatch_manifest`. |
| `test.csv` | 1,600 held-out dispatch packets with the same public context columns and incident narrative, without `dispatch_manifest`. |
| `sample_submission.csv` | Example submission containing every test `case_id` and a valid JSON ranking format. |

## Public Columns

| Column | Type | Present In | Description |
|---|---|---|---|
| `case_id` | string | train, test, submission | Hashed packet identifier. |
| `district_context` | string | train, test | Coarse utility area description, such as a booster district, downtown cast-iron zone, or hospital-commercial corridor. |
| `report_style` | string | train, test | Narrative style used in the incident packet: field log digest, lab exception summary, customer-call synthesis, after-action fragment, or shift handoff note. |
| `incident_count` | integer | train, test | Number of candidate incidents in the packet. This is always 4. |
| `incident_report` | string | train, test | Natural-language packet containing Incident A, B, C, and D. Each incident includes issue language, service context, evidence source, spread, time state, conflict notes, mitigation state, and crew ETA language. |
| `dispatch_manifest` | string | train only, submission | JSON object with `ranked_incidents`, a list of A, B, C, and D ordered from highest to lowest response priority. |

## Hidden Columns In Raw And Private Data

These columns are not included in `test.csv`, but they are present in raw generation output or private answers so the grader can compute the official score:

| Column | Type | Description |
|---|---|---|
| `priority_score_A`, `priority_score_B`, `priority_score_C`, `priority_score_D` | float | Hidden priority score for each incident. Higher means the incident should appear earlier in the manifest. |
| `dominant_hazard` | string | Primary hazard family of the highest-priority incident. |
| `service_context` | string | Service context of the highest-priority incident, such as hospital, dialysis, care home, or ordinary residential service. |
| `evidence_tier` | string | Evidence type of the highest-priority incident, such as lab-confirmed, field-meter, customer cluster, operator log, contractor report, or SCADA-only. |
| `spread_band` | string | Spread of the highest-priority incident: single premise, block, neighborhood, or pressure zone. |
| `difficulty_tier` | string | Generator difficulty bucket: easy, medium, or hard. |

## Data Characteristics

The task requires more than sentiment or keyword matching. High-priority incidents often combine acute microbial or pressure-risk language, sensitive service users, wider geographic spread, strong evidence, active exposure, and unresolved mitigation. Lower-priority incidents may contain alarming words but also have clear repeat samples, duplicate-ticket notes, sensor-only evidence, or completed isolation.

The held-out test split emphasizes harder cases with close priority scores, mixed evidence, and report styles that differ from the simplest training packets. The private score includes hidden worst-group robustness over hazard, service context, evidence tier, spread, and difficulty groups, making simple phrase lookup or majority-prior approaches unreliable.

## License And Source

The dataset is synthetic and generated locally for this benchmark. It may be released under CC0 1.0 Public Domain. Use the GitHub repository containing `generate_raw.py` and `data.csv` as the source URL.
