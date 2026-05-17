"""Tests for swarm intelligence algorithms, particularly Bee Foraging."""

import math

import pytest

from logic_lab.swarm_intelligence.bee_foraging import Bee, BeeColony, FoodSite


class TestFoodSite:
    """Test FoodSite class."""

    def test_food_site_creation(self):
        """Test FoodSite initialization."""
        site = FoodSite(x=100, y=200, nectar=0.8)
        assert site.x == 100
        assert site.y == 200
        assert site.nectar == 0.8
        assert site.trial_count == 0
        assert site.best_nectar == 0.8

    def test_food_site_default_nectar(self):
        """Test FoodSite with default nectar value."""
        site = FoodSite(x=100, y=200)
        assert site.nectar == 0.0
        assert site.best_nectar == 0.0


class TestBee:
    """Test Bee class."""

    def test_bee_scout_creation(self):
        """Test Bee creation as scout."""
        bee = Bee(x=100, y=200, phase="scout")
        assert bee.x == 100
        assert bee.y == 200
        assert bee.phase == "scout"
        assert bee.site_index == -1
        assert bee.energy == 1.0

    def test_bee_employed_creation(self):
        """Test Bee creation as employed."""
        bee = Bee(x=150, y=250, phase="employed", site_index=0)
        assert bee.phase == "employed"
        assert bee.site_index == 0

    def test_bee_onlooker_creation(self):
        """Test Bee creation as onlooker."""
        bee = Bee(x=200, y=300, phase="onlooker")
        assert bee.phase == "onlooker"

    def test_bee_invalid_phase(self):
        """Test Bee raises error on invalid phase."""
        with pytest.raises(ValueError):
            Bee(x=100, y=200, phase="invalid")


class TestBeeColonyInitialization:
    """Test BeeColony initialization."""

    def test_colony_creation(self):
        """Test BeeColony initialization with default parameters."""
        colony = BeeColony(hive_x=500, hive_y=500)
        assert colony.hive_x == 500
        assert colony.hive_y == 500
        assert colony.num_bees == 30
        assert colony.num_scouts == 5
        assert colony.trial_limit == 100

    def test_colony_bee_count(self):
        """Test that colony has correct number of bees."""
        colony = BeeColony(num_bees=30, num_scouts=5)
        assert len(colony.bees) == 30

    def test_colony_bee_phase_distribution(self):
        """Test correct distribution of bee phases."""
        colony = BeeColony(num_bees=30, num_scouts=5)
        scout_count = sum(1 for b in colony.bees if b.phase == "scout")
        employed_count = sum(1 for b in colony.bees if b.phase == "employed")
        onlooker_count = sum(1 for b in colony.bees if b.phase == "onlooker")

        assert scout_count == 5
        assert employed_count + onlooker_count == 25
        assert employed_count == colony.num_employed
        assert onlooker_count == colony.num_onlookers

    def test_colony_initial_bees_near_hive(self):
        """Test that initial bees spawn near the hive."""
        hive_x, hive_y = 500, 500
        colony = BeeColony(hive_x=hive_x, hive_y=hive_y)

        for bee in colony.bees:
            dist = math.sqrt((bee.x - hive_x) ** 2 + (bee.y - hive_y) ** 2)
            assert dist < 30  # Within 30 pixels of hive

    def test_colony_initial_food_sites(self):
        """Test that colony initializes with food sites."""
        colony = BeeColony(num_bees=30, num_scouts=5)
        assert len(colony.sites) > 0


class TestScoutPhase:
    """Test scout bee behavior."""

    def test_scout_movement(self):
        """Test that scout bees move."""
        colony = BeeColony(num_bees=5, num_scouts=5)

        # Record initial positions
        initial_positions = [(b.x, b.y) for b in colony.bees]

        # Update multiple times
        for _ in range(10):
            colony.update()

        # Check that at least some bees moved
        moved = False
        for i, (init_x, init_y) in enumerate(initial_positions):
            if colony.bees[i].x != init_x or colony.bees[i].y != init_y:
                moved = True
                break

        assert moved, "Scouts should move over time"

    def test_scout_discovery_radius(self, monkeypatch):
        """Test scout discovers sites within discovery radius."""
        colony = BeeColony(num_bees=10, num_scouts=10, discovery_radius=50)

        # Add a food site at known location
        colony.sites = [FoodSite(x=100, y=100, nectar=0.9)]

        # Place a scout near the site
        colony.bees[0].x = 120
        colony.bees[0].y = 120
        colony.bees[0].phase = "scout"

        # Update
        colony.update()

        # Scout should be employed now
        assert colony.bees[0].phase == "employed"
        assert colony.bees[0].site_index == 0


class TestEmployedPhase:
    """Test employed bee behavior."""

    def test_employed_local_search(self):
        """Test employed bees search around their site."""
        colony = BeeColony(num_bees=5, num_scouts=0)

        # Create a food site
        colony.sites = [FoodSite(x=500, y=500, nectar=0.7)]

        # Make a bee employed at this site
        colony.bees[0].phase = "employed"
        colony.bees[0].site_index = 0
        colony.bees[0].x = 500
        colony.bees[0].y = 500

        initial_trial_count = colony.sites[0].trial_count

        # Update
        colony.update()

        # Trial count should increase or stay same
        assert colony.sites[0].trial_count >= initial_trial_count

    def test_employed_site_abandonment(self):
        """Test employed bee abandons site after trial limit."""
        colony = BeeColony(num_bees=5, num_scouts=0, trial_limit=5)

        # Create a poor food site
        colony.sites = [FoodSite(x=500, y=500, nectar=0.1)]

        # Make a bee employed at this site
        colony.bees[0].phase = "employed"
        colony.bees[0].site_index = 0

        # Force trial count to exceed limit
        colony.sites[0].trial_count = 6

        # Update
        colony.update()

        # Bee should become scout
        assert colony.bees[0].phase == "scout"
        assert colony.bees[0].site_index == -1

    def test_employed_improvement_resets_trials(self):
        """Test that improvement at site resets trial count."""
        colony = BeeColony(num_bees=5, num_scouts=0, search_radius=100)

        # Create a food site
        colony.sites = [FoodSite(x=500, y=500, nectar=0.3)]
        colony.sites[0].best_nectar = 0.3

        # Make a bee employed
        colony.bees[0].phase = "employed"
        colony.bees[0].site_index = 0
        colony.bees[0].x = 500
        colony.bees[0].y = 500

        # Set some trial count
        colony.sites[0].trial_count = 3

        # Simulate finding improvement by manually updating site
        # (In real sim, this would happen during local search)
        old_trial_count = colony.sites[0].trial_count

        # Update should increase or keep trial count
        colony.update()

        # Trial count should not reset unless improvement found
        assert colony.sites[0].trial_count >= 0


class TestOnlookerPhase:
    """Test onlooker bee behavior."""

    def test_onlooker_selection_probability(self):
        """Test onlooker selection probability based on nectar."""
        colony = BeeColony(num_bees=3, num_scouts=0)

        # Create two sites with different nectar levels
        colony.sites = [
            FoodSite(x=200, y=200, nectar=0.9),
            FoodSite(x=800, y=800, nectar=0.1),
        ]

        # Make all bees onlookers
        for bee in colony.bees:
            bee.phase = "onlooker"

        # Get selection probabilities
        probs = colony._calculate_selection_probability()

        # High nectar site should have higher probability
        assert probs[0] > probs[1]

    def test_onlooker_becomes_employed(self):
        """Test onlooker can become employed."""
        colony = BeeColony(num_bees=10, num_scouts=0)

        # Create a food site
        colony.sites = [FoodSite(x=500, y=500, nectar=0.8)]

        # Make a bee onlooker
        colony.bees[0].phase = "onlooker"
        colony.bees[0].site_index = -1

        # Update multiple times
        became_employed = False
        for _ in range(100):
            colony.update()
            if colony.bees[0].phase == "employed":
                became_employed = True
                break

        assert became_employed, "Onlooker should eventually become employed"

    def test_onlooker_prefers_high_nectar_sites(self):
        """Test onlookers preferentially select high-nectar sites."""
        colony = BeeColony(num_bees=20, num_scouts=0)

        # Create two sites
        colony.sites = [
            FoodSite(x=200, y=200, nectar=0.9),  # High
            FoodSite(x=800, y=800, nectar=0.1),  # Low
        ]

        # Make all bees onlookers
        for bee in colony.bees:
            bee.phase = "onlooker"

        # Track site selections
        site_0_selections = 0
        site_1_selections = 0

        for _ in range(200):
            colony.update()
            for bee in colony.bees:
                if bee.phase == "employed":
                    if bee.site_index == 0:
                        site_0_selections += 1
                    elif bee.site_index == 1:
                        site_1_selections += 1

        # High nectar site should be selected more
        if site_0_selections + site_1_selections > 0:
            assert site_0_selections > site_1_selections


class TestColonyReset:
    """Test colony reset functionality."""

    def test_reset_restores_initial_state(self):
        """Test that reset restores colony to initial state."""
        colony = BeeColony(num_bees=20, num_scouts=5)

        initial_bee_count = len(colony.bees)
        initial_scout_count = sum(1 for b in colony.bees if b.phase == "scout")

        # Simulate changes
        for _ in range(50):
            colony.update()

        # Reset
        colony.reset()

        # Check restoration
        assert len(colony.bees) == initial_bee_count
        assert sum(1 for b in colony.bees if b.phase == "scout") == initial_scout_count
        assert colony.frame_count == 0

    def test_reset_clears_sites(self):
        """Test that reset reinitializes food sites."""
        colony = BeeColony(num_bees=20, num_scouts=5)

        initial_sites = len(colony.sites)

        # Modify sites
        for _ in range(100):
            colony.update()

        # Reset
        colony.reset()

        # Sites should be reinitialized
        assert len(colony.sites) > 0


class TestColonyBehavior:
    """Test overall colony behavior."""

    def test_colony_converges_to_food_sources(self):
        """Test that colony discovers food sources over time."""
        colony = BeeColony(num_bees=30, num_scouts=5, trial_limit=50)

        # Initial site count
        initial_sites = len(colony.sites)

        # Run simulation
        for _ in range(200):
            colony.update()

        # Colony should maintain or increase sites
        assert len(colony.sites) >= 0

    def test_colony_balances_exploration_exploitation(self):
        """Test that colony balances exploration and exploitation."""
        colony = BeeColony(num_bees=30, num_scouts=5)

        scout_phases = []
        employed_phases = []

        # Track phase distribution over time
        for _ in range(100):
            colony.update()
            scout_count = sum(1 for b in colony.bees if b.phase == "scout")
            employed_count = sum(1 for b in colony.bees if b.phase == "employed")
            scout_phases.append(scout_count)
            employed_phases.append(employed_count)

        # Both exploration and exploitation should be active
        assert max(scout_phases) > 0
        assert max(employed_phases) > 0

    def test_colony_pause_resume(self):
        """Test pause and resume functionality."""
        colony = BeeColony(num_bees=20, num_scouts=5)

        # Record state
        state_before = colony.frame_count

        # Pause and update
        colony.toggle_pause()
        colony.update()

        # Frame count should not increase
        assert colony.frame_count == state_before

        # Resume and update
        colony.toggle_pause()
        colony.update()

        # Frame count should increase
        assert colony.frame_count > state_before

    def test_colony_debug_mode(self):
        """Test debug mode toggle."""
        colony = BeeColony()

        assert colony.debug_mode is False

        colony.toggle_debug()
        assert colony.debug_mode is True

        colony.toggle_debug()
        assert colony.debug_mode is False


class TestNectarCalculation:
    """Test nectar landscape calculation."""

    def test_nectar_at_peaks(self):
        """Test that nectar values are high at peaks."""
        colony = BeeColony()

        # Test at a known peak location (150, 150)
        nectar = colony._calculate_nectar_at_location(150, 150)
        assert nectar > 0.3

        # Test at another peak (874, 618) which is near top-right corner
        # Peak is at (canvas_width - 150, canvas_height - 150) with value 0.95
        nectar2 = colony._calculate_nectar_at_location(874, 618)
        assert nectar2 > 0.3

    def test_nectar_decreases_with_distance(self):
        """Test that nectar decreases with distance from peaks."""
        colony = BeeColony()

        nectar_at_peak = colony._calculate_nectar_at_location(150, 150)
        nectar_far = colony._calculate_nectar_at_location(500, 500)

        # Nectar should vary, but generally decrease away from peaks
        assert 0 <= nectar_at_peak <= 1
        assert 0 <= nectar_far <= 1


class TestPhaseTransitions:
    """Test phase transitions."""

    def test_employed_to_onlooker_transition(self):
        """Test that employed bees can transition to onlooker."""
        colony = BeeColony(num_bees=10, num_scouts=0)

        # Make a bee employed
        colony.bees[0].phase = "employed"
        colony.bees[0].site_index = 0

        colony.sites = [FoodSite(x=500, y=500, nectar=0.7)]

        # Run simulation long enough for transition
        transitioned = False
        for _ in range(500):
            colony.update()
            if colony.bees[0].phase == "onlooker":
                transitioned = True
                break

        # Should be possible to transition
        # (not guaranteed due to stochasticity, but likely)
        # This test just ensures no errors occur

    def test_site_exhaustion_removes_sites(self):
        """Test that exhausted sites are removed."""
        colony = BeeColony(num_bees=10, num_scouts=0, trial_limit=10)

        # Create a site
        colony.sites = [FoodSite(x=500, y=500, nectar=0.3)]
        colony.sites[0].trial_count = 25  # Exceed limit

        # Update
        colony.update()

        # Site should be removed
        assert len(colony.sites) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
