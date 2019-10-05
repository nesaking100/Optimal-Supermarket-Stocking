import numpy as np, random, operator, pandas as pd, matplotlib.pyplot as plt, itertools
from pulp import *

data = pd.read_csv('FoodstuffTravelTimes.csv', index_col=0)
data2 = pd.read_csv('FoodstuffLocations.csv', index_col=1)
data3 = pd.read_csv('weekdaydemand.csv', index_col=0)

class Location:
    def __init__(self, lat, lon, name, demand):
        self.lat = lat
        self.lon = lon
        self.name = name
        self.demand = demand
    
    def distance(self, city):
        return data[city.name][self.name]

class Fitness:
    def __init__(self, route):
        self.route = route
        self.distance = 0
        self.fitness = 0.0
    
    def route_demand(self):
        demand = 0
        for location in self.route:
            demand += location.demand
        return demand

    def route_distance(self):
        if self.distance ==0:
            path_distance = 0
            for i in range(0, len(self.route)):
                from_city = self.route[i]
                to_city = None
                if i + 1 < len(self.route):
                    to_city = self.route[i + 1]
                else:
                    to_city = self.route[0]
                path_distance += from_city.distance(to_city)
            self.distance = path_distance
        return self.distance
    
    def route_fitness(self):
        if self.fitness == 0:
            self.fitness = 1 / float(self.route_distance())
        return self.fitness

def create_route(city_list):
    return random.sample(city_list, len(city_list))

def initial_population(pop_size, city_list):
    population = []

    for i in range(0, pop_size):
        population.append(create_route(city_list))
    return population

def rank_routes(population):
    fitness_results = {}
    for i in range(0,len(population)):
        fitness_results[i] = Fitness(population[i]).route_fitness()
    return sorted(fitness_results.items(), key = operator.itemgetter(1), reverse = True)

def selection(pop_ranked, elite_size):
    selection_results = []
    df = pd.DataFrame(np.array(pop_ranked), columns=["Index","Fitness"])
    df['cum_sum'] = df.Fitness.cumsum()
    df['cum_perc'] = 100*df.cum_sum/df.Fitness.sum()
    
    for i in range(0, elite_size):
        selection_results.append(pop_ranked[i][0])
    for i in range(0, len(pop_ranked) - elite_size):
        pick = 100*random.random()
        for i in range(0, len(pop_ranked)):
            if pick <= df.iat[i,3]:
                selection_results.append(pop_ranked[i][0])
                break
    return selection_results

def mating_pool(population, selection_results):
    matingpool = []
    for i in range(0, len(selection_results)):
        index = selection_results[i]
        matingpool.append(population[index])
    return matingpool

def breed(parent1, parent2):
    child = []
    childP1 = []
    childP2 = []
    
    geneA = int(random.random() * len(parent1))
    geneB = int(random.random() * len(parent1))
    
    start_gene = min(geneA, geneB)
    end_gene = max(geneA, geneB)

    for i in range(start_gene, end_gene):
        childP1.append(parent1[i])
        
    childP2 = [item for item in parent2 if item not in childP1]

    child = childP1 + childP2
    return child

def breed_population(matingpool, elite_size):
    children = []
    length = len(matingpool) - elite_size
    pool = random.sample(matingpool, len(matingpool))

    for i in range(0,elite_size):
        children.append(matingpool[i])
    
    for i in range(0, length):
        child = breed(pool[i], pool[len(matingpool)-i-1])
        children.append(child)
    return children

def mutate(individual, mutation_rate):
    for swapped in range(len(individual)):
        if(random.random() < mutation_rate):
            swapWith = int(random.random() * len(individual))
            
            city1 = individual[swapped]
            city2 = individual[swapWith]
            
            individual[swapped] = city2
            individual[swapWith] = city1
    return individual

def mutate_population(population, mutation_rate):
    mutated_pop = []
    
    for ind in range(0, len(population)):
        mutated_ind = mutate(population[ind], mutation_rate)
        mutated_pop.append(mutated_ind)
    return mutated_pop

def next_generation(current_gen, elite_size, mutation_rate):
    pop_ranked = rank_routes(current_gen)
    selection_Results = selection(pop_ranked, elite_size)
    matingpool = mating_pool(current_gen, selection_Results)
    children = breed_population(matingpool, elite_size)
    next_generation = mutate_population(children, mutation_rate)
    return next_generation

def genetic_algorithm(population, pop_size, elite_size, mutation_rate, generations):
    pop = initial_population(pop_size, population)
    # print("Initial distance: " + str(1 / rank_routes(pop)[0][1]))
    # progress = []
    # progress.append(1 / rank_routes(pop)[0][1])
    
    for i in range(0, generations):
        pop = next_generation(pop, elite_size, mutation_rate)
        # progress.append(1 / rank_routes(pop)[0][1])
        # print(1 / rank_routes(pop)[0][1])
    
    # plt.plot(progress)
    # plt.ylabel('Distance')
    # plt.xlabel('Generation')
    # plt.show()
    # plt.close()

    # print("Final distance: " + str(1 / rank_routes(pop)[0][1]))
    bestRouteIndex = rank_routes(pop)[0][0]
    bestRoute = pop[bestRouteIndex]
    return bestRoute

def plot_route(route):
    for _, row in data2.iterrows():
        plt.plot(row.Long, row.Lat, 'ko')

    prev_lon = route[0].lon
    prev_lat = route[0].lat

    for i in range(1, len(route)):
        plt.arrow(prev_lon, prev_lat, route[i].lon - prev_lon, route[i].lat - prev_lat, length_includes_head=True, ec='r', fc='r')
        prev_lon = route[i].lon
        prev_lat = route[i].lat

    plt.arrow(prev_lon, prev_lat, route[0].lon - prev_lon, route[0].lat - prev_lat, length_includes_head=True, ec='r', fc='r')

    plt.show()

class Progress:
    def __init__(self, max_iterations):
        self.iteration = 0
        self.max_iterations = max_iterations
        print(f'\nProgress: [{"#" * round(50 * 0) + "-" * round(50 * (1-0))}] {100. * 0:.2f}% ({self.iteration}/{self.max_iterations})\r', end='')
        
    def increment(self):
        self.iteration += 1
        frac = self.iteration / self.max_iterations
        print(f'Progress: [{"#" * round(50 * frac) + "-" * round(50 * (1-frac))}] {100. * frac:.2f}% ({self.iteration}/{self.max_iterations})\r', end='')

def gen_route(max_demand, route_locations, distances, left_nodes):
    # while route is not up to capacity
    total_demand = route_locations[1].demand
    j = 0
    while total_demand < max_demand and j < len(left_nodes):
        location_index = distances[j]
        location_name = left_nodes[location_index]
        location_demand = data3.demand[location_name]
        if (total_demand + location_demand) <= max_demand:
            route_locations.append(Location(lat=data2["Lat"][location_name], lon=data2["Long"][location_name], name=location_name, demand = location_demand))
            total_demand += route_locations[-1].demand
        j += 1

    route = genetic_algorithm(population=route_locations, pop_size=20, elite_size=5, mutation_rate=0.05, generations=25)
    if total_demand > 12:
        print(f"ERROR: {total_demand} greater than {max_demand}!")
    progress.increment()

    return route

warehouse_location = Location(lat=data2["Lat"]["Warehouse"], lon=data2["Long"]["Warehouse"], name="Warehouse", demand=0)
demand_nodes = [name for name in data.columns if name not in ["Warehouse"]]

routes = []

progress = Progress(len(demand_nodes) * 12 * 24)
iterations = 0
for node in demand_nodes:
    target_location = Location(lat=data2["Lat"][node], lon=data2["Long"][node], name=node, demand = data3.demand[node])

    left_nodes = [name for name in demand_nodes if name not in [node]]

    distance_results = {}

    for i in range(0,len(left_nodes)):
        distance_results[i] = data[left_nodes[i]][node]
    distances = sorted(distance_results.items(), key = operator.itemgetter(1))
    distances = [i[0] for i in distances]

    permutations = list(itertools.permutations(distances[:4]))
    
    for demand in range(1, 13):
        for permutation in permutations:
            distances[:4] = permutation
            routes.append(gen_route(demand, [warehouse_location, target_location], distances, left_nodes))


number_routes = len(routes)
routes.extend(routes)

variables = LpVariable.dicts("Route", [i for i in range(0, len(routes))], None, None, LpBinary)

problem = LpProblem("VRP Testing", LpMinimize)

coefficents = []

for route in routes:
    time = Fitness(route).route_distance()
    time += Fitness(route).route_demand() * 300
    time /= 3600.0
    
    if time > 4.0:
        if len(coefficents) < number_routes:
            # Cost per 4 hour segment
            coefficents.append(1200 * ((time // 4) + 1))
        else:
            # Route should not be allowed
            coefficents.append(1000000.0)
    else:
        if len(coefficents) < number_routes:
            coefficents.append(round(time, 1) * 150.0)
        else:
            coefficents.append(1200.0)

problem += lpSum([coefficents[i] * variables[i] for i in variables])


for location in demand_nodes:
    testing = np.zeros(len(variables))

    for i in range(0, len(variables)):
        if location in [route.name for route in routes[i]]:
            testing[i] = 1

    problem += lpSum([testing[i] * variables[i] for i in variables]) == 1

problem += lpSum([variables[i] for i in range(number_routes)]) <= 20

problem.writeLP("testing.lp")
problem.solve()

print(f"Status: {LpStatus[problem.status]}")
# for var in problem.variables():
#     print(var.name, "=", var.varValue)

print(f"Total Cost: ${value(problem.objective)}")

plt.style.use('ggplot')
fig, ax1 = plt.subplots(figsize=(10, 5))

for index, row in data2.iterrows():
    ax1.plot(row.Long, row.Lat, 'ko')
    ax1.annotate(f"{data3.demand[index] if index != 'Warehouse' else 0}, {index}", xy=(row.Long, row.Lat), xytext=(row.Long - 0.01, row.Lat + 0.003))


chosen_routes = [int(route.name[6:]) for route in problem.variables() if route.varValue > 0.1]

for route_index in chosen_routes:
    route = routes[route_index]
    color = (random.random(), random.random(), random.random())
    prev_lon = route[0].lon
    prev_lat = route[0].lat

    for i in range(1, len(route)):
        plt.arrow(prev_lon, prev_lat, route[i].lon - prev_lon, route[i].lat - prev_lat, length_includes_head=True, ec=color, fc=color)
        prev_lon = route[i].lon
        prev_lat = route[i].lat

    ax1.arrow(prev_lon, prev_lat, route[0].lon - prev_lon, route[0].lat - prev_lat, length_includes_head=True, ec=color, fc=color)


plt.savefig("plot1.png", dpi = 300, bbox_inches='tight')
plt.show()
