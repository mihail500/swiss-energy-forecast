# Portfolio completion checklist

Goal: present an understandable, reproducible forecasting project that the author can explain and modify independently in a junior data science interview. Completion is defined by the deliverables below, rather than an estimated percentage.

## Completed analytical foundation

- [x] Define the hourly energy target, units, next-day horizon, and forecast issue time.
- [x] Obtain 2022-2025 source workbooks and record their provenance and hashes.
- [x] Implement reusable loading, timestamp preparation, and hourly aggregation.
- [x] Check continuity, daylight saving, complete hourly observations, and energy preservation.
- [x] Compare simple baselines using consistent hours and metrics.
- [x] Identify publication constraints and distinguish hindsight benchmarks from availability-policy comparisons.
- [x] Fit calendar-only and calendar-plus-holiday models.
- [x] Investigate errors and holiday-coefficient sensitivity.
- [x] Complete the predefined October-December 2025 comparison.
- [x] Execute and save the consolidated model notebook in a fresh kernel at the session-7 checkpoint.

## 1. Close the data and evaluation gaps

- [x] Investigate pre-2025 timestamp labels using workbook metadata or primary documentation. The earlier endpoints support interval ends; the 2025 manual explicitly documents interval starts. The unresolved earlier convention and its consequences are recorded in `docs/data_assumptions.md`.
- [x] Make the preparation function accept an explicit interval-start/interval-end convention and use it for 2025 in notebook 03. Verify equivalence with the earlier preparation paths on all four source workbooks.
- [x] Document publication and revisions separately from the assumed maturity policy. Rechecked the publisher's documentation on October 23, 2026; historical release vintages remain an explicit limitation.

Done when a reviewer can follow the source-to-target conversion and understand exactly which availability claims the evaluation supports.

## 2. Make reproduction straightforward

- [x] Verify setup and the main evaluation in a separate clean environment: `.venv-check` installation, dependency consistency, all 22 tests, and the 25-cell evaluation passed. A separately restored checkout was not tested.
- [x] Provide a documented command to execute the main comparison and save its outputs. The runner executes 25 code cells, including the export step, and checks all eight overall model rows against the checkpoint. This also passed in the clean environment.
- [x] Extract shared preparation, calendar/holiday features, availability policy, validated overall/subset scoring, provenance, and reporting. Keep the OLS fit steps visible in the experiment notebook for interpretation.
- [x] Clearly distinguish main notebooks from preserved historical snapshots in the README and reproduction guide.

Done when a reviewer can reproduce the comparison by following the documented steps and obtain the recorded metrics to their displayed precision.

## 3. Present the findings

- [x] Write the final report in `reports/final_report.md`.
- [x] Export three labelled figures: overall metrics, monthly MAE, and a forecast week selected by a fixed calendar rule.
- [x] Explain the changed ranking between development and later evaluation, distinguishing measured results from possible explanations.
- [x] Rewrite the README as a portfolio entry point, agreeing with the report and reproduced metrics.

Done when someone can understand the main finding in a few minutes and trace it to the underlying analysis.

## 4. Demonstrate independent ownership

- [ ] Explain the target, issue time, UTC/local-time distinction, maturity policy, and chronological evaluation without reading a script.
- [ ] Explain MAE, RMSE, signed error, ordinary least squares, and the holiday feature's limitations.
- [ ] Reproduce one baseline and its MAE independently, then explain the code.
- [ ] Make and debug a small change to the workflow independently.
- [x] Draft a short project description, interview prompts, and evidence-based CV bullets in `docs/interview_guide.md`. The author still needs to practise and verify ownership independently.

Done when the author can defend the decisions and explain the implementation, including its limitations.

## Optional extensions

Another model, weather inputs, a dashboard, or deployment can be added if they answer a specific question. They are not required to complete the current portfolio scope. Before evaluating changes motivated by the 2025 results, select and record another untouched period and its data-availability rules. Do not silently reuse inspected quarters as independent tests.

## Next working session

The portfolio implementation, report, and clean-environment evaluation are verified. Remaining release work: review the final report personally, complete the independent ownership exercises, and save a reviewed Git checkpoint. Historical timestamp semantics and revision vintages remain documented research limitations, not silently resolved facts. No new model or deployment is required for this scope.
