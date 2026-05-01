# Simulation Directory Classification Proposal

## Recommended Structure: Hybrid Approach

```
logic-lab/
├── examples/                              # Nature of Code examples (existing)
│   ├── chapter_02_forces/
│   ├── chapter_05_steering/
│   ├── chapter_06_physics/
│   ├── chapter_08_fractals/
│   ├── chapter_09_genetic_algorithms/
│   │   ├── ga_shakespeare/
│   │   ├── ga_shakespeare_annotated/
│   │   ├── smart_rockets/
│   │   ├── interactive_selection/
│   │   └── evolving_bloops/
│   ├── chapter_10_neural_networks/
│   │   ├── perceptron_with_normalization/
│   │   └── gesture_classifier/
│   └── chapter_11_neural_networks_ga/
│       ├── flappy_bird/
│       ├── flappy_bird_neuro_evolution/
│       ├── smart_rockets_neuro_evolution/
│       ├── neuro_evolution_steering_seek/
│       ├── creature_sensors/
│       └── neuroevolution_ecosystem/
│
├── algorithms/                            # Standalone algorithms
│   ├── neat_python/                      # NEAT (to be added)
│   │   ├── neat_xor/
│   │   ├── neat_flappy_bird/
│   │   └── neat_ecosystem/
│   ├── genetic_algorithm/                 # General GA utilities
│   │   ├── base_ga.py
│   │   └── ga_utils.py
│   └── neural_network/                    # Custom NN utilities
│       ├── perceptron.py
│       └── feedforward_network.py
│
└── research/                              # Custom experiments/variations
    ├── hybrid_approaches/                 # Combining multiple techniques
    ├── parameter_studies/                 # Testing different parameters
    └── custom_environments/               # Novel ecosystem designs
```

## Alternative Option A: Algorithm-First Structure

```
logic-lab/
├── algorithms/
│   ├── genetic_algorithms/
│   │   ├── ga_shakespeare/
│   │   ├── smart_rockets/
│   │   ├── interactive_selection/
│   │   └── evolving_bloops/
│   │
│   ├── neural_networks/
│   │   ├── perceptron_with_normalization/
│   │   └── gesture_classifier/
│   │
│   ├── neuro_evolution/
│   │   ├── flappy_bird_neuro_evolution/
│   │   ├── smart_rockets_neuro_evolution/
│   │   ├── neuro_evolution_steering_seek/
│   │   ├── creature_sensors/
│   │   └── neuroevolution_ecosystem/
│   │
│   └── neat_python/                      # To be added
│       ├── neat_xor/
│       ├── neat_flappy_bird/
│       └── neat_ecosystem/
│
├── fundamentals/                          # Basic concepts
│   ├── forces/                            # Chapter 2
│   ├── steering_behaviors/                # Chapter 5
│   ├── physics/                           # Chapter 6
│   └── fractals/                          # Chapter 8
│
└── research/
```

## Alternative Option B: Learning Paradigm Structure

```
logic-lab/
├── supervised_learning/
│   └── gesture_classifier/
│
├── unsupervised_learning/
│   └── (future dimensionality reduction, clustering)
│
├── evolutionary_algorithms/
│   ├── genetic_algorithms/
│   │   ├── ga_shakespeare/
│   │   ├── smart_rockets/
│   │   ├── interactive_selection/
│   │   └── evolving_bloops/
│   │
│   └── neuro_evolution/
│       ├── flappy_bird_neuro_evolution/
│       ├── smart_rockets_neuro_evolution/
│       ├── neuro_evolution_steering_seek/
│       ├── creature_sensors/
│       └── neuroevolution_ecosystem/
│
├── reinforcement_learning/
│   └── (future: Q-learning, policy gradient)
│
├── nature_of_code/
│   └── (all basic examples)
│
└── advanced/
    ├── neat_python/
    └── hybrid_approaches/
```

---

## Recommendation: Hybrid (Option 1)

**Why this structure:**

1. **`examples/`** → Preserves the Nature of Code source material organization
   - Clear mapping to original chapters
   - Easy to add new examples from the book
   - Educational trajectory preserved (students learn in book order)

2. **`algorithms/`** → Implementations and research tools
   - `neat_python/` stands alone as a distinct algorithm
   - Reusable algorithm utilities
   - Clear separation between examples and implementations

3. **`research/`** → Custom experiments
   - Your own variations and hybrid approaches
   - Parameter sensitivity studies
   - Novel use cases

**Benefits:**
- ✅ Scalable: Can easily add neat-python, RL algorithms, etc.
- ✅ Clear: Easy for someone new to understand the organization
- ✅ Flexible: Supports examples → algorithms → research progression
- ✅ Modular: Can reuse code from `algorithms/` across directories
- ✅ Future-proof: Room for new paradigms (RL, meta-learning, etc.)

---

## Migration Path

If you choose the Recommended structure, here's how to reorganize:

```bash
# Step 1: Create new directory structure
mkdir -p examples/{chapter_02,chapter_05,chapter_06,chapter_08,chapter_09,chapter_10,chapter_11}
mkdir -p algorithms/{neat_python,genetic_algorithm,neural_network}
mkdir -p research/{hybrid_approaches,parameter_studies,custom_environments}

# Step 2: Move existing simulations
mv simulation/random_walk examples/chapter_02_forces/
mv simulation/ga_shakespeare examples/chapter_09_genetic_algorithms/
mv simulation/perceptron_with_normalization examples/chapter_10_neural_networks/
# ... (continue for all files)

# Step 3: Create utility modules
touch algorithms/genetic_algorithm/base_ga.py
touch algorithms/neural_network/feedforward_network.py
# ... (extract reusable code)
```

---

## Naming Convention Additions

Regardless of directory structure, consider standardizing file names:

```
# Format: {type}_{domain}_{variant}.py

# Genetic Algorithms
ga_shakespeare.py
ga_shakespeare_annotated.py
ga_interactive_selection.py

# Neural Networks
nn_perceptron.py
nn_gesture_classifier.py

# Neuro-Evolution
ne_flappy_bird.py
ne_steering_seek.py
ne_ecosystem.py

# NEAT
neat_xor.py
neat_flappy_bird.py
```

This makes file purpose clear at a glance and groups related files alphabetically.
