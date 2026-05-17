"""
Comprehensive test suite for the Gray-Scott reaction-diffusion system.

Tests cover:
- Grid initialization and boundary conditions
- Laplacian computation accuracy
- Single step updates and numerical stability
- Pattern formation and convergence behavior
- Parameter range validation
"""

# Import the Gray-Scott module
import sys
from pathlib import Path

import numpy as np
import pytest
import scipy.ndimage

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from logic_lab.reaction_diffusion.gray_scott import gray_scott


class TestGridInitialization:
    """Test suite for grid initialization."""

    def test_grid_size_correct(self):
        """Test that grids are initialized with correct dimensions."""
        U, V = gray_scott.initialize_grids()

        assert U.shape == (gray_scott.GRID_SIZE, gray_scott.GRID_SIZE)
        assert V.shape == (gray_scott.GRID_SIZE, gray_scott.GRID_SIZE)
        assert U.shape == V.shape

    def test_u_values_in_valid_range(self):
        """Test that U concentrations are within valid range [0, 1]."""
        U, V = gray_scott.initialize_grids()

        assert np.all(U >= 0.0), "U contains negative values"
        assert np.all(U <= 1.0), "U contains values > 1"

    def test_v_values_in_valid_range(self):
        """Test that V concentrations are within valid range [0, 1]."""
        U, V = gray_scott.initialize_grids()

        assert np.all(V >= 0.0), "V contains negative values"
        assert np.all(V <= 1.0), "V contains values > 1"

    def test_u_starts_near_one(self):
        """Test that U is initialized mostly to 1.0 (with small noise)."""
        U, V = gray_scott.initialize_grids()

        mean_u = np.mean(U)
        assert 0.9 < mean_u < 1.1, f"U mean {mean_u} is not close to 1.0"

    def test_v_starts_near_zero(self):
        """Test that V is initialized mostly to 0.0 except in center."""
        U, V = gray_scott.initialize_grids()

        # Most of V should be near zero
        num_zero_cells = np.sum(V < 0.01)
        total_cells = gray_scott.GRID_SIZE**2
        ratio_zero = num_zero_cells / total_cells

        assert ratio_zero > 0.8, f"Only {ratio_zero:.1%} of V is near zero"

    def test_v_center_perturbation_exists(self):
        """Test that V has a perturbation in the center region."""
        U, V = gray_scott.initialize_grids()

        center = gray_scott.GRID_SIZE // 2
        radius = gray_scott.GRID_SIZE // 8
        y, x = np.ogrid[: gray_scott.GRID_SIZE, : gray_scott.GRID_SIZE]
        mask = (x - center) ** 2 + (y - center) ** 2 <= radius**2

        max_v_in_center = np.max(V[mask])
        assert max_v_in_center > 0.1, f"Center V perturbation too weak: {max_v_in_center}"

    def test_grids_are_different_instances(self):
        """Test that multiple initializations create independent grids."""
        U1, V1 = gray_scott.initialize_grids()
        U2, V2 = gray_scott.initialize_grids()

        # Grids should have same structure but different random noise
        assert U1.shape == U2.shape
        assert V1.shape == V2.shape
        # Due to seeding, these should actually be identical
        # This tests deterministic initialization
        assert np.allclose(U1, U2)
        assert np.allclose(V1, V2)


class TestLaplacianComputation:
    """Test suite for Laplacian calculation."""

    def test_laplacian_kernel_shape(self):
        """Test that the Laplacian kernel has correct shape."""
        kernel = gray_scott.LAPLACIAN_KERNEL
        assert kernel.shape == (3, 3)

    def test_laplacian_kernel_sums_to_zero(self):
        """Test that the Laplacian kernel sums to zero (conservative)."""
        kernel = gray_scott.LAPLACIAN_KERNEL
        assert np.isclose(np.sum(kernel), 0.0)

    def test_laplacian_uniform_field_is_zero(self):
        """Test that Laplacian of uniform field is zero."""
        field = np.ones((gray_scott.GRID_SIZE, gray_scott.GRID_SIZE))
        laplacian = gray_scott.calculate_laplacian(field)

        # For uniform field, Laplacian should be ~0 (allowing for edge effects)
        assert np.allclose(laplacian, 0.0, atol=1e-6)

    def test_laplacian_output_shape_matches_input(self):
        """Test that Laplacian output has same shape as input."""
        field = np.random.random((gray_scott.GRID_SIZE, gray_scott.GRID_SIZE))
        laplacian = gray_scott.calculate_laplacian(field)

        assert laplacian.shape == field.shape

    def test_laplacian_detects_gradient(self):
        """Test that Laplacian detects regions with concentration gradients."""
        # Create a simple test field: high in center, low elsewhere
        field = np.zeros((50, 50))
        field[20:30, 20:30] = 1.0

        laplacian = gray_scott.calculate_laplacian(field)

        # At the boundary, Laplacian should be non-zero
        boundary_laplacian = laplacian[19:31, 19:31]
        assert np.any(boundary_laplacian != 0.0), "Laplacian should detect boundary"

    def test_laplacian_of_smooth_field(self):
        """Test Laplacian on a smooth Gaussian-like field."""
        x = np.linspace(-5, 5, gray_scott.GRID_SIZE)
        y = np.linspace(-5, 5, gray_scott.GRID_SIZE)
        xx, yy = np.meshgrid(x, y)

        # Gaussian field
        field = np.exp(-(xx**2 + yy**2) / 2)
        laplacian = gray_scott.calculate_laplacian(field)

        # For Gaussian, Laplacian should be largest near center and edges
        assert np.isfinite(laplacian).all(), "Laplacian contains NaN or Inf"

    def test_laplacian_periodic_boundary_conditions(self):
        """Test that wrap mode creates periodic boundary conditions."""
        # Create a field with high value at corner
        field = np.zeros((10, 10))
        field[0, 0] = 1.0
        field[9, 9] = 1.0

        laplacian = gray_scott.calculate_laplacian(field)

        # Corner pixels should have non-zero Laplacian due to wrap-around
        # The pixel at (0,0) should "see" (9,9) and (9,0) and (0,9) as neighbors
        assert laplacian[0, 0] != 0.0, "Wrap-around not working at corner"


class TestUpdateStep:
    """Test suite for the update step computation."""

    def test_update_step_preserves_grid_shape(self):
        """Test that update_step doesn't change grid dimensions."""
        gray_scott.U, gray_scott.V = gray_scott.initialize_grids()
        original_shape_u = gray_scott.U.shape
        original_shape_v = gray_scott.V.shape

        gray_scott.update_step()

        assert gray_scott.U.shape == original_shape_u
        assert gray_scott.V.shape == original_shape_v

    def test_update_step_changes_values(self):
        """Test that update_step actually modifies the grids."""
        gray_scott.U, gray_scott.V = gray_scott.initialize_grids()
        U_before = gray_scott.U.copy()
        V_before = gray_scott.V.copy()

        gray_scott.update_step()

        # At least some values should change
        assert not np.allclose(gray_scott.U, U_before), "U values didn't change"
        assert not np.allclose(gray_scott.V, V_before), "V values didn't change"

    def test_update_step_no_nan_values(self):
        """Test that update_step doesn't introduce NaN values."""
        gray_scott.U, gray_scott.V = gray_scott.initialize_grids()

        # Run multiple steps
        for _ in range(10):
            gray_scott.update_step()
            assert np.isfinite(gray_scott.U).all(), "U contains NaN"
            assert np.isfinite(gray_scott.V).all(), "V contains NaN"

    def test_update_step_no_inf_values(self):
        """Test that update_step doesn't introduce infinite values."""
        gray_scott.U, gray_scott.V = gray_scott.initialize_grids()

        for _ in range(10):
            gray_scott.update_step()
            assert np.all(np.abs(gray_scott.U) < 1e10), "U contains Inf"
            assert np.all(np.abs(gray_scott.V) < 1e10), "V contains Inf"

    def test_update_step_maintains_bounds(self):
        """Test that clamping keeps values in [0, 1] range."""
        gray_scott.U, gray_scott.V = gray_scott.initialize_grids()

        for _ in range(100):
            gray_scott.update_step()

            assert np.all(gray_scott.U >= 0.0), "U below 0"
            assert np.all(gray_scott.U <= 1.0), "U above 1"
            assert np.all(gray_scott.V >= 0.0), "V below 0"
            assert np.all(gray_scott.V <= 1.0), "V above 1"

    def test_update_step_reaction_term_affects_change(self):
        """Test that the reaction term (U*V*V) affects the update."""
        gray_scott.U, gray_scott.V = gray_scott.initialize_grids()
        U_before = gray_scott.U.copy()

        # Set up a region where U and V are significant
        gray_scott.U[100:110, 100:110] = 0.5
        gray_scott.V[100:110, 100:110] = 0.5

        gray_scott.update_step()

        # U in high-V region should decrease (due to -U*V*V term)
        assert np.mean(gray_scott.U[100:110, 100:110]) < 0.5


class TestPatternFormation:
    """Test suite for pattern formation and long-term behavior."""

    def test_pattern_forms_over_time_spots(self):
        """Test that spots pattern forms from initial conditions."""
        gray_scott.F = gray_scott.PRESETS["spots"]["F"]
        gray_scott.k = gray_scott.PRESETS["spots"]["k"]
        gray_scott.U, gray_scott.V = gray_scott.initialize_grids()

        # Run simulation
        for _ in range(500):
            gray_scott.update_step()

        # After sufficient steps, V should have localized regions
        max_v = np.max(gray_scott.V)
        min_v = np.min(gray_scott.V)
        variance_v = np.var(gray_scott.V)

        assert max_v > 0.1, "Pattern not forming (max V too low)"
        assert variance_v > 0.001, "Pattern not forming (low variance)"

    def test_pattern_forms_over_time_stripes(self):
        """Test that stripes pattern forms from initial conditions."""
        gray_scott.F = gray_scott.PRESETS["stripes"]["F"]
        gray_scott.k = gray_scott.PRESETS["stripes"]["k"]
        gray_scott.U, gray_scott.V = gray_scott.initialize_grids()

        # Run simulation
        for _ in range(500):
            gray_scott.update_step()

        # After sufficient steps, should have structure
        variance_v = np.var(gray_scott.V)
        assert variance_v > 0.001, "Stripes pattern not forming"

    def test_pattern_forms_over_time_waves(self):
        """Test that waves pattern forms from initial conditions."""
        gray_scott.F = gray_scott.PRESETS["waves"]["F"]
        gray_scott.k = gray_scott.PRESETS["waves"]["k"]
        gray_scott.U, gray_scott.V = gray_scott.initialize_grids()

        # Run simulation
        for _ in range(500):
            gray_scott.update_step()

        # After sufficient steps, should have structure
        variance_v = np.var(gray_scott.V)
        assert variance_v > 0.001, "Waves pattern not forming"

    def test_system_doesnt_diverge(self):
        """Test that the system remains stable over long simulation."""
        gray_scott.U, gray_scott.V = gray_scott.initialize_grids()

        # Run for 2000 steps
        for _ in range(2000):
            gray_scott.update_step()

            # Check for divergence
            assert np.max(gray_scott.U) <= 1.0
            assert np.max(gray_scott.V) <= 1.0
            assert np.isfinite(gray_scott.U).all()
            assert np.isfinite(gray_scott.V).all()


class TestParameterRanges:
    """Test suite for parameter range validation and behavior."""

    def test_parameter_preset_spots(self):
        """Test that spots preset parameters are valid."""
        F = gray_scott.PRESETS["spots"]["F"]
        k = gray_scott.PRESETS["spots"]["k"]

        assert 0.0 <= F <= 0.1, f"Invalid F for spots: {F}"
        assert 0.0 <= k <= 0.1, f"Invalid k for spots: {k}"

    def test_parameter_preset_stripes(self):
        """Test that stripes preset parameters are valid."""
        F = gray_scott.PRESETS["stripes"]["F"]
        k = gray_scott.PRESETS["stripes"]["k"]

        assert 0.0 <= F <= 0.1, f"Invalid F for stripes: {F}"
        assert 0.0 <= k <= 0.1, f"Invalid k for stripes: {k}"

    def test_parameter_preset_waves(self):
        """Test that waves preset parameters are valid."""
        F = gray_scott.PRESETS["waves"]["F"]
        k = gray_scott.PRESETS["waves"]["k"]

        assert 0.0 <= F <= 0.1, f"Invalid F for waves: {F}"
        assert 0.0 <= k <= 0.1, f"Invalid k for waves: {k}"

    def test_different_presets_produce_different_behaviors(self):
        """Test that different presets have different parameter values."""
        F_spots = gray_scott.PRESETS["spots"]["F"]
        F_stripes = gray_scott.PRESETS["stripes"]["F"]
        F_waves = gray_scott.PRESETS["waves"]["F"]

        # At least F values should differ
        assert len(set([F_spots, F_stripes, F_waves])) >= 2, "Presets too similar"

    def test_extreme_f_values_dont_crash(self):
        """Test that extreme F values don't cause crashes."""
        gray_scott.U, gray_scott.V = gray_scott.initialize_grids()

        # Test with very low F
        gray_scott.F = 0.001
        for _ in range(10):
            gray_scott.update_step()
        assert np.isfinite(gray_scott.U).all() and np.isfinite(gray_scott.V).all()

        # Test with moderate-high F
        gray_scott.F = 0.08
        for _ in range(10):
            gray_scott.update_step()
        assert np.isfinite(gray_scott.U).all() and np.isfinite(gray_scott.V).all()

    def test_extreme_k_values_dont_crash(self):
        """Test that extreme k values don't cause crashes."""
        gray_scott.U, gray_scott.V = gray_scott.initialize_grids()

        # Test with very low k
        gray_scott.k = 0.001
        for _ in range(10):
            gray_scott.update_step()
        assert np.isfinite(gray_scott.U).all() and np.isfinite(gray_scott.V).all()

        # Test with high k
        gray_scott.k = 0.09
        for _ in range(10):
            gray_scott.update_step()
        assert np.isfinite(gray_scott.U).all() and np.isfinite(gray_scott.V).all()

    def test_diffusion_coefficients_are_positive(self):
        """Test that diffusion coefficients have correct values."""
        assert gray_scott.Du > 0, "Du should be positive"
        assert gray_scott.Dv > 0, "Dv should be positive"
        assert gray_scott.Du > gray_scott.Dv, "Du should be larger than Dv"

    def test_time_step_is_positive(self):
        """Test that time step is positive."""
        assert gray_scott.dt > 0, "dt should be positive"


class TestColorMapping:
    """Test suite for V-to-color conversion."""

    def test_color_mapping_zero_concentration(self):
        """Test color for zero V concentration."""
        r, g, b = gray_scott.v_to_color(0.0)
        assert 0 <= r <= 255
        assert 0 <= g <= 255
        assert 0 <= b <= 255
        # Low concentration should be darker
        assert b > 50, "Low V should have blue component"

    def test_color_mapping_full_concentration(self):
        """Test color for full V concentration."""
        r, g, b = gray_scott.v_to_color(1.0)
        assert r > 200, "High V should have significant red"
        assert g > 200, "High V should have significant green"
        assert b > 200, "High V should have significant blue"

    def test_color_mapping_monotonic(self):
        """Test that color value increases monotonically with V."""
        v_values = np.linspace(0.0, 1.0, 10)
        colors = [gray_scott.v_to_color(v) for v in v_values]
        intensities = [(r + g + b) / 3 for r, g, b in colors]

        # Intensities should be non-decreasing
        for i in range(len(intensities) - 1):
            assert intensities[i] <= intensities[i + 1]

    def test_color_mapping_range(self):
        """Test that all color components are in valid RGB range."""
        for v in np.linspace(0.0, 1.0, 20):
            r, g, b = gray_scott.v_to_color(v)
            assert 0 <= r <= 255, f"Invalid R for v={v}: {r}"
            assert 0 <= g <= 255, f"Invalid G for v={v}: {g}"
            assert 0 <= b <= 255, f"Invalid B for v={v}: {b}"
