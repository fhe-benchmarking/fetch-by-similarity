# Measurements

When running `python ./harness/run_submission.py <some-variant>`, it will generate measurement files in a sub-directory under this directory.
Specifically, the sub-directories that it uses are `small`, `medium` and `large` for the fetch-payload variants, and `count_small`, `count_medium` and `count_large` for the count-matches variants.
If it is run with argument `--num_runs <n>` it will generate `<n>` measurements files called `results-1.json`, ..., `results-<n>.json`, all in the same sub-directory.

Before submitting your implementation, run the `run_submission.py` script with argument `--num_runs 3` for each variant of the workload that you want to submit. Then commit all these results file to your fork, the average of these three runs will be the numbers reported for your submission.

## Results for the reference implementation

For the reference implementation we only produced measurements for the small and medium instances, both count-matches and fetch-payloads.
You can find these measurements in the sub-directories here, they were generated in February 2026 on an [EC2 instance type I7ie.24xl](https://aws.amazon.com/ec2/instance-types/i7i/).
(The fetch-payloads timing were obtained on I7ie.metal-24xl, but similar runs on I7ie.24xl were only about 2% slower.)
