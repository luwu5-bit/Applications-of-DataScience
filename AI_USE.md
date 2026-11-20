# AI use log

Required disclosure under WU guidelines. One line per use.

| Date | Tool | Used for |
|---|---|---|
| 2026-11-14 | Claude Code (Claude Fable 5.2) | Project scaffolding: directory structure, config, module stubs with signatures, test skeletons from the toy example, ASSUMPTIONS.md and README drafts |
| 2026-11-14 | Claude Code (Claude Fable 5.2) | Implemented matrix factorization (numpy ALS) with tests and the training script; downloaded MovieLens 1M; ran the regularization sweep documented in ASSUMPTIONS.md |
| 2026-11-14 | Claude Code (Claude Fable 5.2) | Implemented Pareto pools, aggregators (AVG, LM, NPO, XPO), metrics, group sampling and the experiment runner with tests; ran E1; diagnostic runs and the comparison with the paper in docs/replication_notes.md |
| 2026-11-14 | Claude Code (Claude Fable 5.2) | Ran E2, E3 and E5 and summarised them in docs/replication_notes.md; wrote scripts/make_figures.py and generated the figures |
| 2026-11-15 | Claude Code (Claude Fable 5.2) | Checked all figures against a fresh recomputation; drafted the presentation slides and speaker notes (presentation/group_fairness_presentation.pptx) |
| 2026-11-15 | Claude (chat) and Claude Code (Claude Fable 5.2) | Cross-checked ASSUMPTIONS.md against the paper text; added the "Paper says" and "Status" columns |
| 2026-11-15 | Claude Code (Claude Fable 5.2) | Diagnostic run for A5 (SIM groups by similarity to the whole group instead of the seed); result written to docs/replication_notes.md |
| 2026-11-15 | Claude Code (Claude Fable 5.2) | Switched nDCG gain (A11) and SIM group building (A5) back to the paper, updated tests, reran E1/E2/E3/E5, regenerated figures, updated notes and slides; diagnostic run with tied ranks (A4) |
| 2026-11-15 | Claude Code (Claude Fable 5.2) | Switched ranks to tied ranks (A4) and reran E1/E2/E3/E5; diagnostics on tie order, MF random start, rating matrix and nDCG gain; rewrote docs/replication_notes.md, regenerated figures, updated slides and notes |
| 2026-11-16 | Claude Code (Claude Fable 5.2) | Merged the work into main; added the AI use slide to the presentation |
| 2026-11-18 | Claude Code (Claude Opus 5.5) | Presentation preparation (speaker notes, checking claims against the six-fit data); averaging all experiments over 20 MF fits, Average without Misery (AWM) baseline with tests, summary and figure scripts, AWM threshold diagnostic, documentation of A15 to A17; rating-based metrics no_misery and rating (A18); paper baselines MUL, MAX, BORDA, MED (A19) |
| 2026-11-20 | Claude Code (Claude Opus 5.5) | Commit of the 20-fit work; after the presentation feedback: nDCG with linear gain (A20) and rerun, SIM group similarity diagnostic and draft paragraph, softened the m = 8 claim in the notes |
| 2026-11-20 | Claude Code (Claude Opus 5.5) | First draft of the report (report/report.tex) and the figure xpo_lead_by_metric.png |
| 2026-11-21 | Claude Code (Claude Opus 5.5) | Report: code appendix with reproduction commands, SIM paragraph linked to the Unit 4 slides and Baltrunas et al. (2010), trimmed main text back to 5 pages |
