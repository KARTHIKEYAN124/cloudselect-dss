# Evaluation

The automated suite checks arithmetic against a manual AWS cost and weighted-score example; each mandatory constraint; security evidence; normalized and invalid weights; missing ratings; tie handling; all API routes; and scenario outcomes.

Expected scenario winners with the shipped illustrative dataset:

| Scenario | Winner | Explanation |
| --- | --- | --- |
| Baseline | GCP | Strong cost and management contributions |
| Cost-sensitive startup | GCP | Only configuration inside the €80 ceiling |
| Security-sensitive application | Azure | Only fixture with customer-managed keys evidence |
| Growing application | AWS | Scalability and performance weights outweigh cost |

Use the What-if screen to inspect winner stability under each +10 percentage point change. A €1 budget, 4-vCPU minimum, or unsupported region must produce no recommendation. These checks establish implementation correctness under the demo assumptions; they do not validate real-world provider superiority.
