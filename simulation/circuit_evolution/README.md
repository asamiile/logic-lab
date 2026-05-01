# Circuit Evolution - NEAT

Circuit design using NEAT (NeuroEvolution of Augmenting Topologies).

## Run Commands

### Run Circuit NEAT

```bash
source .venv/Scripts/activate
python simulation/circuit_evolution/experiments/design/run_circuit_neat.py -p 50
```

### Draw Results
```bash
# Draw all genomes
python simulation/circuit_evolution/experiments/design/draw_circuit_neat.py test_draw

# Draw a specific genome ID (for example: genome ID 6620)
python simulation/circuit_evolution/experiments/design/draw_circuit_neat.py test_draw -s <GENOME_ID>
```

Genome IDs are available in this folder:
```
simulation/circuit_evolution/experiments/design/out/circuit_neat/<experiment_name>/genome/
```

## File Structure

- `environment/` - Circuit evaluation environment
- `experiments/design/` - NEAT-based circuit design experiments
