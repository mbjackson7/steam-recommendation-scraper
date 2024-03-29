import json
import re
import networkx as nx
import time
import random
from collections import Counter
from operator import itemgetter

import matplotlib as mpl
import matplotlib.pyplot as plt

class StopCondition(StopIteration):
    pass
class Simulation:
    '''Simulate state transitions on a network'''

    def __init__(self, G, initial_state, state_transition,
            stop_condition=None, name=''):
        '''
        Create a Simulation instance.

        Args:
            G: a networkx.Graph instance.
            initial_state: function with signature `initial_state(G)`, that
                accepts a single argument, the Graph, and returns a dictionary
                of all node states. The keys in this dict should be node names
                and the values the corresponding initial node state.
            state_transition: function with signature
                `state_transition(G, current_state)` that accepts two
                arguments, the Graph and a dictionary of current node states,
                and returns a dictionary of updated node states. The keys in
                this dict should be node names and the values the corresponding
                updated node state.
            stop_condition (optional): function with signature
                `stop_condition(G, current_state)` that accepts two arguments,
                the Graph and a dictionary of current node states, and returns
                True if the simulation should be stopped at its current state.

        Keyword Args:
            name (optional): a string used in titles of plots and drawings.

        Raises:
            ValueError: if not all graph nodes have an initial state.
        '''
        self.G = G.copy()
        self._initial_state = initial_state
        self._state_transition = state_transition
        self._stop_condition = stop_condition
        # It's okay to specify stop_condition=False
        if stop_condition and not callable(stop_condition):
            raise TypeError("'stop_condition' should be a function")
        self.name = name or 'Simulation'

        self._states = []
        self._value_index = {}
        self._cmap = plt.cm.get_cmap('tab10')

        self._initialize()

        self._pos = nx.layout.spring_layout(G)

    def _append_state(self, state):
        self._states.append(state)
        # Update self._value_index
        for value in set(state.values()):
            if value not in self._value_index:
                self._value_index[value] = len(self._value_index)

    def _initialize(self):
        if self._initial_state:
            if callable(self._initial_state):
                state = self._initial_state(self.G)
            else:
                state = self._initial_state
            nx.set_node_attributes(self.G, state, 'state')

        if any(self.G.nodes[n].get('state') is None for n in self.G.nodes):
            raise ValueError('All nodes must have an initial state')

        self._append_state(state)

    def _step(self):
        # We're choosing to use the node attributes as the source of truth.
        # This allows the user to manually perturb the network in between steps.
        state = nx.get_node_attributes(self.G, 'state')
        if self._stop_condition and self._stop_condition(self.G, state):
            raise StopCondition
        state = nx.get_node_attributes(self.G, 'state')
        new_state = self._state_transition(self.G, state)
        state.update(new_state)
        nx.set_node_attributes(self.G, state, 'state')
        self._append_state(state)

    def _categorical_color(self, value):
        index = self._value_index[value]
        node_color = self._cmap(index)
        return node_color

    @property
    def steps(self):
        ''' Returns the number of steps the sumulation has run '''
        return len(self._states) - 1

    def state(self, step=-1):
        '''
        Get a state of the simulation; by default returns the current state.

        Args:
            step: the step of the simulation to return. Default is -1, the
            current state.

        Returns:
            Dictionary of node states.

        Raises:
            IndexError: if `step` argument is greater than the number of steps.
        '''
        try:
            return self._states[step]
        except IndexError:
            raise IndexError('Simulation step %i out of range' % step)

    def draw(self, step=-1, labels=None, **kwargs):
        '''
        Use networkx.draw to draw a simulation state with nodes colored by
        their state value. By default, draws the current state.

        Args:
            step: the step of the simulation to draw. Default is -1, the
            current state.
            kwargs: keyword arguments are passed to networkx.draw()

        Raises:
            IndexError: if `step` argument is greater than the number of steps.
        '''
        state = self.state(step)
        node_colors = [self._categorical_color(state[n]) for n in self.G.nodes]
        nx.draw(self.G, pos=self._pos, node_color=node_colors, **kwargs)

        if labels is None:
            labels = sorted(set(state.values()), key=self._value_index.get)
        patches = [mpl.patches.Patch(color=self._categorical_color(l), label=l)
                   for l in labels]
        plt.legend(handles=patches)

        if step == -1:
            step = self.steps
        if step == 0:
            title = 'initial state'
        else:
            title = 'step %i' % (step)
        if self.name:
            title = '{}: {}'.format(self.name, title)
        plt.title(title)

    def plot(self, min_step=None, max_step=None, labels=None, **kwargs):
        '''
        Use pyplot to plot the relative number of nodes with each state at each
        simulation step. By default, plots all simulation steps.

        Args:
            min_step: the first step of the simulation to draw. Default is
                None, which plots starting from the initial state.
            max_step: the last step, not inclusive, of the simulation to draw.
                Default is None, which plots up to the current step.
            labels: ordered sequence of state values to plot. Default is all
                observed state values, approximately ordered by appearance.
            kwargs: keyword arguments are passed along to plt.plot()

        Returns:
            Axes object for the current plot
        '''
        x_range = range(min_step or 0, max_step or len(self._states))
        counts = [Counter(s.values()) for s in self._states[min_step:max_step]]
        if labels is None:
            labels = {k for count in counts for k in count}
            labels = sorted(labels, key=self._value_index.get)

        for label in labels:
            series = [count.get(label, 0) / sum(count.values()) for count in counts]
            plt.plot(x_range, series, label=label, **kwargs)

        title = 'node state proportions'
        if self.name:
            title = '{}: {}'.format(self.name, title)
        plt.title(title)
        plt.xlabel('Simulation step')
        plt.ylabel('Proportion of nodes')
        plt.legend()
        plt.xlim(x_range.start)

        return plt.gca()

    def run(self, steps=1):
        '''
        Run the simulation one or more steps, as specified by the `steps`
        argument. Default is to run a single step.

        Args:
            steps: number of steps to advance the simulation.
        '''
        for _ in range(steps):
            try:
                self._step()
            except StopCondition as e:
                print(
                    "Stop condition met at step %i." % self.steps
                    )
                break


# SIS functions
def initial_state(G):
    state = {}
    for node in G.nodes:
        state[node] = 'S'
    
    patient_zero = random.choice(list(G.nodes))
    state[patient_zero] = 'I'
    return state

MU = 0.2
BETA = 0.1

def state_transition(G, current_state, mode='SIS'):
    next_state = {}
    for node in G.nodes:
        if current_state[node] == 'I':
            if random.random() < MU:
                if mode == 'SIS':
                    next_state[node] = 'S'
                elif mode == 'SIR':
                    next_state[node] = 'R'
        elif current_state[node] == 'S':
            for neighbor in G.neighbors(node):
                if current_state[neighbor] == 'I':
                    if random.random() < BETA:
                        next_state[node] = 'I'

    return next_state

def get_state_lists(G, current_state):
    susceptibles = []
    infectees = []
    recovered = []
    for node in G.nodes:
        if current_state[node] == 'I':
            infectees.append(node)
        elif current_state[node] == 'S':
            susceptibles.append(node)
        else:
            recovered.append(node)
    return susceptibles, infectees, recovered

def run_sis(G, iterations=10):
    current_state = initial_state(G)
    _, infectees, _ = get_state_lists(G, current_state)
    patient_zero = infectees[0]
    for _ in range(iterations):
        current_state = state_transition(G, current_state)
    susceptibles, infectees, recovered = get_state_lists(G, current_state)
    return patient_zero, len(susceptibles), len(infectees), len(recovered)

def run_sir(G, iterations=10):
    current_state = initial_state(G)
    _, infectees, _ = get_state_lists(G, current_state)
    patient_zero = infectees[0]
    for _ in range(iterations):
        current_state = state_transition(G, current_state, mode='SIR')
    susceptibles, infectees, recovered = get_state_lists(G, current_state)
    return patient_zero, len(susceptibles), len(infectees), len(recovered)

def spreading_analysis(G, probability=0.2, iterations=10):
    
    def spread(root, G, node, probability, currIter, iterations, spreads):
        if currIter >= iterations:
            return
        for neighbor in G.neighbors(node):
            if random.random() < probability:
                spreads[root].append(neighbor)
                spread(root, G, neighbor, probability, currIter + 1, iterations, spreads)

    spreads = {}
    for node in G.nodes():
        currIter = 0
        spreads[node] = []
        spread(node, G, node, probability, currIter, iterations, spreads)
        
    return spreads
                
def main():
    VERSION = "0.0.1"
    G = nx.DiGraph()

    print("Welcome to Steam Recommendation Analyzer v" + VERSION)

    oldGraphName = input("Graph name? ")
    G = nx.read_gexf(f"./.graphs/{oldGraphName}")
    print("Loading graph...")
    print("Loaded graph with " + str(len(G.nodes())) + " nodes")
    nodeCount = int(oldGraphName.split("-")[0].replace("steam", ""))
    recCount = int(oldGraphName.split("-")[1])
    
    print("Analyzing graph...")
    print("Graph has " + str(len(G.nodes())) + " nodes")
    print("Graph has " + str(len(G.edges())) + " edges")
    print("Graph has " + str(nx.number_weakly_connected_components(G)) + " weakly connected components")
    print("Graph has " + str(nx.number_strongly_connected_components(G)) + " strongly connected components")
    print("Graph has " + str(nx.number_connected_components(G.to_undirected())) + " connected components")
    
    print("Calculating degree centrality...")
    degreeCentrality = nx.degree_centrality(G)
    print("Degree centrality is " + str(degreeCentrality))
    print("Calculating betweenness centrality...")
    betweennessCentrality = nx.betweenness_centrality(G)
    print("Betweenness centrality is " + str(betweennessCentrality))
    print("Calculating closeness centrality...")
    closenessCentrality = nx.closeness_centrality(G)
    print("Closeness centrality is " + str(closenessCentrality))

    # print("Calculating spreading...")
    # spreads = spreading_analysis(G)
    
    # sis = {}
    # sir = {}

    # for _ in range(50):
    #     root, susceptibles, infectees, recovered = run_sis(G)
    #     sis[root] = {
    #         "susceptibles": susceptibles,
    #         "infectees": infectees,
    #         "recovered": recovered
    #     }
    #     root, susceptibles, infectees, recovered = run_sir(G)
    #     sir[root] = {
    #         "susceptibles": susceptibles,
    #         "infectees": infectees,
    #         "recovered": recovered
    #     }

    sim = Simulation(G, initial_state, state_transition, name='SIS model')
    sim.run(25)
    sim.draw()
    sim.plot()
            
    print("Saving results...")
    with open(f"./.analysis/{oldGraphName}.json", "w") as f:
        json.dump({
            "degreeCentrality": degreeCentrality,
            "betweennessCentrality": betweennessCentrality,
            "closenessCentrality": closenessCentrality,
        }, f)
        
    print("Done!")
if __name__ == "__main__":
    main()
