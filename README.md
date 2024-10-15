# DiseaseSpreading

## Description

This project contains the implementations of various algorithms aimed at containing the spread of a disease which spreads through the mechanisms of the Linear Threshold model.
The aim is to "vaccinate" some nodes of the network to minimize the spread of the disease. The following methods are implemented for the same:
- Greedy
- Local Search which starts with the greedy solution
- Hill climbing which starts with the greedy solution
- Integer Linear Programming which gives the optimal solution for a given set of network topologies
- Relaxed Linear Programming with top-*k* rounding
- Relaxed Linear Programming with iterative rounding procedure

## Installation

The project requires G++, python, and packages like Numpy, Pandas, Matplotlib, and Gurobipy.

## Usage

- For generating Erdos-Renyi graphs: `python3 LT_generate_ERG.py`
- For generating Gaussian Waxman graphs: `python3 LT_generate_waxman_gaussian.py`
- For running the C++ implementation for greedy, local search, and hill-climbing algorithms in `linear_threshold_greedy_LS_HC.cpp`:
   ```
   g++ -o <executable> linear_threshold_greedy_LS_HC.cpp
   ./<executable> <graph_filename>
   ```
   The same goes for `linear_threshold_greedy.cpp`
- `TX_graph_generator.py` and `NY_graph_generator.py` generate graphs for Texas and New York respectively
  
All the graph generation algorithms require some parameters that are described when needed as user input

