# Measurements

When running `python ./harness/run_submission.py <some-variant>`, it will generate measurement files in a sub-directory under this directory. If it is run with argument `--num_runs <n>` it will generate `<n>` measurements files called `results-1.json`, ..., `results-<n>.json`, all in the same directory.

Before submitting your implementation, run the `run_submission.py` script with argument `--num_runs 3` for each variant of the workload that you want to submit. Then commit all these results file to your fork, the average of these three runs will be the numbers reported for your submission.
