# Workload reference implementation - fetch by similarity

## Security and Parameters

The reference implementation uses CKKS over a ring of dimension 2^16=65,536 (which means that each ciphertext can pack upto 2^15=32,768 slots).
The entire fetch-by-similarity procedure consumes 22 levels, so we need at least a 23-level modulus chain.
This yields a ciphertext modulus of just under 1500 bits (including the auxiliary primes for key switching).
According to Table 5.2 of [Bossuat et al., 2024](https://cic.iacr.org/p/1/4/26), this combination provides more than 128 bits of security.
(According to that table, the largest modulus that provides 128-bit security with N=2^16 has 1747 bits.)

Specifically, the `CCParams` structure of OpenFHE that we use for this procedure is as follows:
```
  cParams.SetSecretKeyDist(UNIFORM_TERNARY);
  cParams.SetKeySwitchTechnique(HYBRID);
  cParams.SetMultiplicativeDepth(23);
  cParams.SetSecurityLevel(HEStd_128_classic);
  cParams.SetScalingTechnique(FLEXIBLEAUTO);
  cParams.SetScalingModSize(42);
  cParams.SetFirstModSize(57);
```
With 42-bit scaling and 57-bit first-modulus size, we can get close to $57-42-1=14$-bit numbers in the slots.
Specifically, in our implementation the payload values are encoded in numbers in the range [0,512] with precision of 1/16, giving us $9+4=13$ bits per value.
One bit is ``wasted'' on calibration (see \cref{sec:compaction}), so we end up with 12 usable bits per slot (even though the harness only puts 9 bits per slot, so the top three bits in our slots will always be zero).

## More Information

More details about this implementation are provided in the [PDF file](https://github.com/fhe-benchmarking/fetch-by-similarity/blob/main/submission/docs/fetch-by-similarity.pdf)
in the `submission/docs` directory.
