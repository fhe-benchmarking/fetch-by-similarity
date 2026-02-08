# Remote Submission Example

This directory contains a remote submission example for the benchmarking suite.

As part of the benchmarking process, all remote backends are expected to make their homomorphic encryption parameters explicit and reviewable, since these parameters directly affect security, performance, and comparability across submissions. Ideally, such parameters should be reported automatically by the backend.

This document provides a static description of the homomorphic encryption parameters used by this example backend, along with a minimal execution trace to illustrate end-to-end operation.

Additional details that can be provided include things like workload structure, level consumption, scale management, parameterization at higher security levels and performance characteristics. You can see an example of such details (for the Lattica submission) at [README_Lattica_submission.md](https://github.com/Lattica-ai/fetch-by-similarity/blob/public_submission/submission_remote/docs/README_Lattica_submission.md).

---

## FHE parameters

The example backend runs in the TOY setting and uses the following homomorphic encryption parameters:

```python
homomorphic_params = {
    "q_bits": 1059,       # 693 compute levels + 366 GHS
    "n": 2 ** 10,         # polynomial degree
    "err_std": 1,         # standard deviation of the encryption noise
    "sk_hw": 64,          # secret key Hamming weight
}
```

These parameters are chosen for simplicity and reproducibility and are not intended to represent a security-hardened or final challenge submission.



---

## Example execution

```
python3 harness/run_submission.py 0 --num_runs 3 --remote
[harness] Running submission for toy dataset
          returning matching payloads
09:22:45 [harness] 1: Dataset generation completed (elapsed: 0.0921s)
09:22:49 [harness] 1.1: Communication: Get cryptographic context completed (elapsed: 4.1561s)
09:22:50 [harness] 2: Dataset preprocessing completed (elapsed: 0.9178s)
09:22:51 [harness] 3: Key Generation completed (elapsed: 1.0182s)
         [harness] Public and evaluation keys size: 17.5M
09:22:59 [harness] 3.1: Communication: Upload evaluation key completed (elapsed: 8.4016s)
09:23:00 [harness] 4: Dataset encoding and encryption completed (elapsed: 1.3202s)
         [harness] Encrypted database size: 45.2M
09:23:10 [harness] 4.1: Communication: Upload encrypted database completed (elapsed: 9.8422s)
09:23:10 [harness] 5: Encrypted dataset preprocessing completed (elapsed: 0.0002s)

         [harness] Run 1 of 3
09:23:10 [harness] 6: Query generation completed (elapsed: 0.0817s)
09:23:10 [harness] 7: Query preprocessing completed (elapsed: 0.0002s)
09:23:11 [harness] 8: Query encryption completed (elapsed: 0.9186s)
         [harness] Encrypted query size: 192.1K
09:23:14 [harness] 9: Encrypted computation completed (elapsed: 3.0995s)
09:23:16 [harness] 10: Result decryption and postprocessing completed (elapsed: 1.8867s)
         [harness] PASS (All 13 payload vectors match)
         [submission] GPU time: 0.233s
         [submission] Queue time: 0.115s
         [submission] Network time: 1.794s
[total latency] 31.7349s

         [harness] Run 2 of 3
09:23:16 [harness] 6: Query generation completed (elapsed: 0.2567s)
09:23:16 [harness] 7: Query preprocessing completed (elapsed: 0.0002s)
09:23:17 [harness] 8: Query encryption completed (elapsed: 0.9503s)
         [harness] Encrypted query size: 192.1K
09:23:21 [harness] 9: Encrypted computation completed (elapsed: 3.1502s)
09:23:22 [harness] 10: Result decryption and postprocessing completed (elapsed: 1.9398s)
         [harness] PASS (All 0 payload vectors match)
         [submission] GPU time: 0.234s
         [submission] Queue time: 0.109s
         [submission] Network time: 1.86s
[total latency] 32.0455s

         [harness] Run 3 of 3
09:23:23 [harness] 6: Query generation completed (elapsed: 0.3535s)
09:23:23 [harness] 7: Query preprocessing completed (elapsed: 0.0002s)
09:23:24 [harness] 8: Query encryption completed (elapsed: 1.0021s)
         [harness] Encrypted query size: 192.1K
09:23:27 [harness] 9: Encrypted computation completed (elapsed: 2.9552s)
09:23:29 [harness] 10: Result decryption and postprocessing completed (elapsed: 1.9179s)
         [harness] PASS (All 16 payload vectors match)
         [submission] GPU time: 0.232s
         [submission] Queue time: 0.106s
         [submission] Network time: 1.661s
[total latency] 31.9773s

All steps completed for the toy dataset!
```

- Public + evaluation keys size: \~17.5 MB
- Encrypted DB size: \~45.2 MB
- Encrypted query size: \~192.1 KB
- Total inference time: 3.0995 s
- Compute inference time: 233 ms
---
