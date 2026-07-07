# Water Network Incident Dispatch Priority

NLP ranking challenge for Eris. Each row is a drinking-water utility incident packet with four anonymized candidate incidents, A through D. Solvers submit a JSON dispatch manifest ranking the incidents from highest to lowest response priority.

Files in this package:

- `dataset.md` - dataset description for the dataset editor
- `problem.md` - challenge prompt for the problem editor
- `prepare.py` - deterministic public/private split
- `grade.py` - weighted pairwise dispatch-order loss
- `config.yaml` - scoring configuration
- `rubrics.yaml` - task-specific rubrics
- `raw/generate_raw.py` - deterministic raw data generator
- `raw/data.csv` - generated after running the generator
- `water-network-incident-dispatch-priority-raw.zip` - raw upload zip, generated locally

