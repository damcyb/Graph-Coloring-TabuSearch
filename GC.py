from collections import deque
from random import randrange
import matplotlib.pyplot as plt
import networkx as nx

def find_max(solution):
    max = 0
    for key in solution:
        if solution[key] > max:
            max = solution[key]
    print max + 1
    return max

def find_min(solution):
    for key in solution:
        if solution[key] > max:
            max = solution[key]
    print max + 1
    return max

def prepare_initial_solution():
    # this function converts dictionary to sorted by vertice number list
    initial_solution_dict = nx.coloring.greedy_color(G, strategy=nx.coloring.strategy_largest_first)
    tmp1 = sorted(initial_solution_dict.iteritems())
    initial_solution_sorted_list = []

    for elem in tmp1:
        initial_solution_sorted_list.append(list(elem))

    for elem in initial_solution_sorted_list:
        elem[0] = int(elem[0])

    initial_solution_sorted_list.sort(key=lambda x: x[0])
    return initial_solution_sorted_list

def tabucol(graph, number_of_colors, previous_solution, first_solution, tabu_size=7, reps=80, max_iterations=10000):
    colors = list(range(number_of_colors))
    iterations = 0
    tabu = deque()

    # Generate a initial solution:
    solution = dict()
    if first_solution:
        initial_solution = prepare_initial_solution()
        for i in range(len(graph)):
            if initial_solution[i][1] < number_of_colors:
                solution[i] = initial_solution[i][1]
            else:
                solution[i] = colors[randrange(0, len(colors))]
    else:
        solution = previous_solution
        for i in range(len(graph)):
            if solution[i] >= number_of_colors:
                solution[i] = colors[randrange(0, len(colors))]

    aspiration_level = dict()

    while iterations < max_iterations:
        move_candidates = set()  # use a set to avoid duplicates
        conflict_count = 0

        for (node_a, node_b) in G.edges:
            if solution[int(node_a) - 1] == solution[int(node_b) - 1]:
                move_candidates.add(int(node_a) - 1)
                move_candidates.add(int(node_b) - 1)
                conflict_count += 1

        move_candidates = list(move_candidates)

        if conflict_count == 0:
            # Found a valid coloring.
            break

        # Generate neighbor solutions.
        new_solution = None
        for r in range(reps):
            node = move_candidates[randrange(0, len(move_candidates))]
            new_color = colors[randrange(0, len(colors) - 1)]
            if solution[node] == new_color:
                new_color = colors[-1]

            new_solution = solution.copy()
            new_solution[node] = new_color
            new_conflicts = 0

            for (node_a, node_b) in G.edges:
                if new_solution[int(node_a) - 1] == new_solution[int(node_b) - 1]:
                    new_conflicts += 1

            if new_conflicts < conflict_count:  # found an improved solution
                if new_conflicts <= aspiration_level.setdefault(conflict_count, conflict_count - 1):
                    aspiration_level[conflict_count] = new_conflicts - 1

                    if (node, new_color) in tabu:
                        tabu.remove((node, new_color))
                        break
                else:
                    if (node, new_color) in tabu:
                        continue
                break

        tabu.append((node, solution[node]))
        if len(tabu) > tabu_size:  # queue full
            tabu.popleft()  # remove the oldest move

        solution = new_solution
        iterations += 1

    if conflict_count != 0:
        print("No coloring found with {} colors.".format(number_of_colors))
        return False
    else:
        print("Found coloring:", solution)
        find_max(solution)
        previous_solution = solution

        return True, previous_solution

def createGraph(file):
    # function reads graph data from file and create graph's structure using networkx library
    is_gonna_read_first_line = True
    G = nx.Graph()
    with open(file) as source_file:
        for line in source_file:
            if not is_gonna_read_first_line:
                graph_edge = line.split()
                G.add_edge(graph_edge[0], graph_edge[1])
            is_gonna_read_first_line = False
    return G

def read_vertices_number(file):
    with open(file) as source_file:
        V = source_file.readline()
    return V

def heuristic_color(nx_graph, k, previous_solution, first_coloring):
    graph = nx.to_numpy_matrix(nx_graph).astype(int).tolist()
    ctn, previous_solution = tabucol(graph, k, previous_solution, first_coloring)
    return ctn, previous_solution

def color_graph(G):
    initial_color = nx.coloring.greedy_color(G, strategy=nx.coloring.strategy_largest_first)
    greedy_color_numbers = find_max(initial_color) + 1
    # greedy_color_numbers = 13
    first_coloring = True
    previous_solution = dict()
    for v in range(greedy_color_numbers, 2, -1):
        ctn, previous_solution = heuristic_color(G, v, previous_solution, first_coloring)
        if not ctn:
            break
        first_coloring = False


if __name__ == "__main__":
    path = "./benchmark/"
    file = path + 'le450_25a_convert.txt'
    G = createGraph(file)
    V = read_vertices_number(file)
    color_graph(G)