
## Introduction
Planning is an important topic in AI because intelligent agents are expected to automatically plan their own actions in uncertain domains. Planning and scheduling systems are commonly used in automation and logistics operations, robotics and self-driving cars, and for aerospace applications like the Hubble telescope and NASA Mars rovers.

This project is split between implementation and analysis. First you will combine symbolic logic and classical search to implement an agent that performs progression search to solve planning problems. Then you will experiment with different search algorithms and heuristics, and use the results to answer questions about designing planning systems.

This is part of my Udacity course on fundamentals of AI.

## Instructions

1. Start by running the example problem (this example implements the "have cake" problem from Fig 10.7 of AIMA 3rd edition). The script will print information about the problem domain and solve it with several different search algorithms, however these algorithms cannot solve larger, more complex problems so next you'll have to implement a few more sophisticated heuristics.

```
$ python example_have_cake.py
```

2. Open `my_planning_graph.py`. Documentation for the planning graph classes is provided in the docstrings and examples [here](examples.md). Refer to the heuristics pseudocode [here](pseudocode/heuristics.md), chapter 10 of AIMA 3rd edition or chapter 11 of AIMA 2nd edition (available [on the AIMA book site](http://aima.cs.berkeley.edu/2nd-ed/newchap11.pdf)) and the detailed instructions inline with each TODO statement for help. You should implement the following functions:

  - `ActionLayer._inconsistent_effects`
  - `ActionLayer._interference`
  - `ActionLayer._competing_needs`
  - `LiteralLayer._inconsistent_support`
  - `LiteralLayer._negation`
  - `PlanningGraph.h_levelsum`
  - `PlanningGraph.h_maxlevel`
  - `PlanningGraph.h_setlevel`

After you complete each function, test your solution by running:

```
$ `python -m unittest -v`
```


3. Experiment with different search algorithms using the `run_search.py` script. (See example usage below.) The goal of your experiment is to understand the tradeoffs in speed, optimality, and complexity of progression search as problem size increases. 

  - Run the search experiment manually (you will be prompted to select problems & search algorithms)
```
$ python run_search.py -m
```

  - You can also run specific problems & search algorithms - e.g., to run breadth first search and UCS on problems 1 and 2. you can select other algorithms by numbers provided in the code:
```
$ python run_search.py -p 1 2 -s 1 2
$ python run_search.py -p 3 -s 1 
```


### Experiment with the planning algorithms

The `run_search.py` script allows you to choose any combination of eleven search algorithms (three uninformed and eight with heuristics) on four air cargo problems. The cargo problem instances have different numbers of airplanes, cargo items, and airports that increase the complexity of the domains.




## (Optional) Project Enhancements

You will find in this project that even trivial planning problems become intractable for domain-independent planning. (The search space for planning problems grows exponentially with problem size.) However, this code can be used as a basis to explore automated planning more deeply by incorporating optimizations or additional planning algorithms (like GraphPlan) to create a more robust planner.

1. Static code optimizations
	- Several optimizations have been omitted for simplicity. For example, the `Expr` class used for symbolic representations of the actions and literals is _very_ slow (the time to do basic operations like negating an object can be 1000x slower than more optimal representations). And the inconsistent effects, interference, and negation mutexes are static for a given problem domain; they do not need to be checked each time a layer is added to the planning graph.

2. Optimize the planning graph implementaion (ref. section 6 [Planning graph as the basis for deriving heuristics
for plan synthesis by state space and CSP search](https://ac.els-cdn.com/S0004370201001588/1-s2.0-S0004370201001588-main.pdf?_tid=571411a9-859b-4a29-83c7-686d44673011&acdnat=1523663582_550f8fef02020c1c90bf6ef1caef3eaa))
    - One way to implement a much faster planning graph uses a bi-level structure to reduce construction time and memory consumption. The complete list of states and complete list of actions are known when the planning graph instance is created (they're static), and the set of static mutexes is also fixed. A single list can be used to track the first layer at which each literal or action enter the planning graph (they will remain in the graph in all future layers), and a single list can be used to track when mutexes first leave the graph (they will remain out of the graph in all future layers).

3. Use a different language
	- Python is slow. Using a faster language can deliver a few orders of magnitude faster performance, which can make non-trivial problem domains feasible. The planning graph is particularly inefficient, in part due to idiosyncrasies of Python with an implementation designed for _clarity_ rather than performance. The [Europa](https://github.com/nasa/europa) planner from NASA should be much faster.

4. Build your own problems
    - The air cargo domain problems implemented for you were chosen to represent various changes in complexity. There are many other problems that you could implement on your own. For example, the block world problem and spare tire problem in the AIMA textbook. You can also find examples online of planning domain problems. Implement one or more problems beyond the air cargo domain and see how your planner works in those domains.


### Additional Search Topics

- Regression search with GraphPlan (ref. [GraphPlan](https://github.com/aimacode/aima-pseudocode/blob/master/md/GraphPlan.md) in the AIMA pseudocode). Regression search can be very fast in some problem domains, but progression search has been more popular in recent years because it is more easily extended to real-world problems, for example to support resource constraints (like planning for battery recharging in mobile robots).

- Progression search with Monte Carlo Tree Search (e.g., ["Using Monte Carlo Tree Search to Solve Planning Problems in Transportation Domains"](https://link.springer.com/chapter/10.1007%2F978-3-642-45111-9_38))
