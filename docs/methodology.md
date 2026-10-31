# Decision methodology

Hard constraints precede ranking: budget, CPU, memory, disk capacity, region, required security evidence, and complete criterion scores. Ineligible configurations retain explanations but have no score or rank. No eligible configurations means no recommendation.

Monthly cost is rounded compute hourly rate × hours, storage rate × requested GB, and egress rate × requested GB. Components are rounded to cents before summation. Rates are illustrative EUR units, not converted live prices.

Cost rating is `1 + 4 * (max_cost - cost) / (max_cost - min_cost)`, based on the full three-configuration reference population. Equal costs receive 5. Keeping this population fixed avoids eligibility filtering changing the normalization reference. All other ratings are explicit illustrative 1–5 assessments with recorded rationales. Higher is always better. Scores are not measurements or compliance proofs.

Weights are normalized by dividing each by the positive total. Score is the sum of normalized weight × rating. Rankings use unrounded scores; ties within 1e-9 receive a shared competition rank. IDs deterministically order tied records without asserting a unique winner. Displayed rounded scores can appear equal when underlying values differ.

Sensitivity increases one normalized weight by 0.10 (capped at 1) and proportionally scales the remaining weights to keep a unit total. An existing 100% weight stays unchanged in its own experiment. Eligibility and costs remain constant. Every experiment records complete weights and scores, winner sets, and whether the winner set changed. Stable winners are meaningful results.

Scores 1–5 represent assumed suitability from least to most suitable within this teaching exercise. They are not an externally validated provider rubric. Missing ratings cause exclusion, never a default favorable value. A production extension should collect independent comparable workload benchmarks, validate qualitative judgments, verify security evidence, and maintain dated regional prices.
