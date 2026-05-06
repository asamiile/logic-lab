# Ford Circles

Draws tangent circles for reduced fractions on the number line.

## Run

```bash
uv run python mathematical/ford_circles/ford_circles.py
```

## Controls

| Key | Effect |
|---|---|
| `+` / `-` | Change maximum denominator |
| `l` | Toggle fraction labels |
| `b` | Toggle baseline |
| `f` | Toggle circle fill |
| `s` | Save screenshot |

## Algorithm

Ford circles place one circle above each reduced fraction `p/q`:

1. **Generate fractions**: List all reduced fractions between `0` and `1` with denominator up to a limit.
2. **Map position**: Place each circle center at `x = p / q`.
3. **Set radius**: Use `r = 1 / (2q^2)`.
4. **Draw tangent circles**: Any two Ford circles are either tangent or disjoint.

The construction is closely related to Farey sequences, continued fractions, and rational approximations. Higher denominators create smaller circles that fill gaps between simpler fractions.

## Other Environments

**TouchDesigner**: Generate reduced fractions in a Python DAT and instance circles with `x = p / q` and radius `1 / (2q^2)`.

**UE5**: Compute fraction records in Blueprint or C++, then render circles as instanced disks or spline rings on a 2D plane.
