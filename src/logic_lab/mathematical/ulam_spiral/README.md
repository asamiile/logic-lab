# Ulam Spiral

Places integers on a square spiral and highlights prime numbers.

## Run

```bash
uv run python mathematical/ulam_spiral/ulam_spiral.py
```

## Controls

| Key | Effect |
|---|---|
| `m` | Switch display mode |
| `+` / `-` | Change residue modulus |
| `l` | Toggle spiral path |
| `s` | Save screenshot |

## Algorithm

The Ulam spiral reveals prime number structure by arranging integers on a grid:

1. **Spiral coordinates**: Start with `1` at the center, then walk right, up, left, and down with increasing step lengths.
2. **Prime sieve**: Use the Sieve of Eratosthenes to mark primes up to the largest grid value.
3. **Prime plot**: Draw only the prime positions, which often form diagonal streaks.
4. **Residue coloring**: Color primes by `n mod m` to expose modular patterns.

The sketch includes a factor-density mode that draws composites faintly, making the prime gaps and diagonal families easier to compare against the full integer lattice.

## Other Environments

**TouchDesigner**: Generate spiral coordinates in a Script CHOP or DAT, mark primes with a sieve, and instance geometry at prime positions. Use `n % m` as a color index.

**UE5**: Build the spiral point set in Blueprint or C++, then draw prime instances with Niagara or Instanced Static Meshes. Material color can be driven by the residue class.
