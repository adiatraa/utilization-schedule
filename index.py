import random
import numpy as np
import csv

class Activity:
    def __init__(self, name, expected_enrollment, preferred_facilitators, other_facilitators):
        self.name = name
        self.expected_enrollment = expected_enrollment
        self.preferred_facilitators = preferred_facilitators
        self.other_facilitators = other_facilitators
        self.room = None
        self.time = None
        self.facilitator = None

class Facilitator:
    def __init__(self, name):
        self.name = name

class Room:
    def __init__(self, name, capacity):
        self.name = name
        self.capacity = capacity

activities = [
    Activity("SLA100A", 50, ["Glen", "Lock", "Banks", "Zeldin"], ["Numen", "Richards"]),
    Activity("SLA100B", 50, ["Glen", "Lock", "Banks", "Zeldin"], ["Numen", "Richards"]),
    Activity("SLA191A", 50, ["Glen", "Lock", "Banks", "Zeldin"], ["Numen", "Richards"]),
    Activity("SLA191B", 50, ["Glen", "Lock", "Banks", "Zeldin"], ["Numen", "Richards"]),
    Activity("SLA201", 50, ["Glen", "Banks", "Zeldin", "Shaw"], ["Numen", "Richards", "Singer"]),
    Activity("SLA291", 50, ["Lock", "Banks", "Zeldin", "Singer"], ["Numen", "Richards", "Shaw", "Tyler"]),
    Activity("SLA303", 60, ["Glen", "Zeldin", "Banks"], ["Numen", "Singer", "Shaw"]),
    Activity("SLA304", 25, ["Glen", "Banks", "Tyler"], ["Numen", "Singer", "Shaw", "Richards", "Uther", "Zeldin"]),
    Activity("SLA394", 20, ["Tyler", "Singer"], ["Richards", "Zeldin"]),
    Activity("SLA449", 60, ["Tyler", "Singer", "Shaw"], ["Zeldin", "Uther"]),
    Activity("SLA451", 100, ["Tyler", "Singer", "Shaw"], ["Zeldin", "Uther", "Richards", "Banks"])
]

facilitators = [Facilitator("Lock"), Facilitator("Glen"), Facilitator("Banks"),
               Facilitator("Richards"), Facilitator("Shaw"), Facilitator("Singer"),
               Facilitator("Uther"), Facilitator("Tyler"), Facilitator("Numen"), Facilitator("Zeldin")]

rooms = [
    Room("Slater 003", 45),
    Room("Roman 216", 30),
    Room("Loft 206", 75),
    Room("Roman 201", 50),
    Room("Loft 310", 108),
    Room("Beach 201", 60),
    Room("Beach 301", 75),
    Room("Logos 325", 450),
    Room("Frank 119", 60)
]

timeslots = [10, 11, 12, 13, 14, 15]

def initialize_population(population_size):
    population = []
    for _ in range(population_size):
        schedule = []
        for activity in activities:
            room = random.choice(rooms)
            time = random.choice(timeslots)
            
            if activity.facilitator is None:
                facilitator = random.choice(facilitators)
            elif activity.facilitator.name in activity.preferred_facilitators:
                facilitator = Facilitator(activity.facilitator.name)
            else:
                facilitator = random.choice(facilitators)
            
            activity.room = room
            activity.time = time
            activity.facilitator = facilitator
            schedule.append(activity)
        population.append(schedule)
    return population

initial_population = initialize_population(500)

def calculate_fitness(schedule):
    fitness = 0.0

    for activity in schedule:
        activity_fitness = 0.0
          
        if any(
            other_activity != activity
            and other_activity.room == activity.room
            and other_activity.time == activity.time
            for other_activity in schedule
        ):
            activity_fitness -= 0.2

        if activity.room.capacity < activity.expected_enrollment:
            activity_fitness -= 0.5
        elif activity.room.capacity > 3 * activity.expected_enrollment:
            activity_fitness -= 0.2
        elif activity.room.capacity > 6 * activity.expected_enrollment:
            activity_fitness -= 0.4
        else:
            activity_fitness += 0.3

        if activity.facilitator.name in activity.preferred_facilitators:
            activity_fitness += 1.0
        elif activity.facilitator.name in activity.other_facilitators:
            activity_fitness += 0.5
        else:
            activity_fitness -= 0.2

        activities_in_same_time_slot = [
            other_activity for other_activity in schedule if other_activity.time == activity.time
        ]
        if len([a for a in schedule if a.facilitator.name == activity.facilitator.name]) > 4:
            activity_fitness -= 0.5
        if 1 <= len([a for a in activities_in_same_time_slot if a.facilitator.name == activity.facilitator.name]) <= 2:
            activity_fitness -= 0.4

        if activity.name in ["SLA100A", "SLA100B", "SLA191A", "SLA191B"]:
            activity_fitness += 0.5  
        elif activity.name == "SLA201":
            activity_fitness += 0.2  
        elif activity.name == "SLA291":
            activity_fitness += 0.2  
        elif activity.name == "SLA303":
            activity_fitness += 0.2  
        elif activity.name == "SLA304":
            activity_fitness += 0.2  
        elif activity.name == "SLA394":
            activity_fitness += 0.2  
        elif activity.name == "SLA449":
            activity_fitness += 0.2  
        elif activity.name == "SLA451":
            activity_fitness += 0.2  

        fitness += activity_fitness



    return fitness

def softmax(x):
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum()

def select_parents(population, num_parents):
    fitness_scores = [calculate_fitness(schedule) for schedule in population]

    softmax_scores = softmax(fitness_scores)

    adjusted_scores = []
    for schedule in population:
        preferred_facilitator_count = sum(
            1 for activity in schedule if activity.facilitator.name in activity.preferred_facilitators
        )
        adjusted_score = softmax_scores[population.index(schedule)] * preferred_facilitator_count
        adjusted_scores.append(adjusted_score)

    selected_parents = random.choices(population, weights=adjusted_scores, k=num_parents)
    return selected_parents


def crossover(parent1, parent2):
    child1 = []
    child2 = []
    crossover_point = random.randint(2, len(parent1))

    child1.extend(parent1[:crossover_point])
    child1.extend(parent2[crossover_point:])
    child2.extend(parent2[:crossover_point])
    child2.extend(parent1[crossover_point:])

    return child1, child2

def mutate(schedule, mutation_rate):
    for activity in schedule:
        if random.random() < mutation_rate:
            activity_to_mutate = random.choice(schedule)
            
            activity_to_mutate.room = random.choice(rooms)
            activity_to_mutate.time = random.choice(timeslots)

            if activity_to_mutate.facilitator.name not in activity_to_mutate.preferred_facilitators and random.random() < 0.2:
                activity_to_mutate.facilitator = random.choice(facilitators)

def genetic_algorithm(population_size, num_generations, mutation_rate):
    population = initialize_population(population_size)

    for generation in range(num_generations):
        parents = select_parents(population, num_parents=len(population) // 2)
        offspring = []

        while len(offspring) < len(population):
            parent1, parent2 = random.sample(parents, k=2)
            child1, child2 = crossover(parent1, parent2)
            mutate(child1, mutation_rate)
            mutate(child2, mutation_rate)
            offspring.extend([child1, child2])

        population = offspring


    best_schedule = max(population, key=calculate_fitness)
    best_fitness = calculate_fitness(best_schedule)
    print("Best Fitness:", best_fitness)

    print("Best Schedule:")
    for activity in best_schedule:
        print(f"{activity.name}: Room - {activity.room.name}, Time - {activity.time}, Facilitator - {activity.facilitator.name}")

    return best_schedule

if __name__ == "__main__":
    population_size = 500
    num_generations = 100
    mutation_rate = 0.01/2
    min_desired_fitness = 0.50

    best_schedule = None
    best_fitness = -float("inf")

    while best_fitness < min_desired_fitness:
        population = initialize_population(population_size)

        for generation in range(num_generations):
            parents = select_parents(population, num_parents=len(population) // 2)
            offspring = []

            while len(offspring) < len(population):
                parent1, parent2 = random.sample(parents, k=2)
                child1, child2 = crossover(parent1, parent2)
                mutate(child1, mutation_rate)
                mutate(child2, mutation_rate)
                offspring.extend([child1, child2])

            population = offspring

            current_best_schedule = max(population, key=calculate_fitness)
            current_best_fitness = calculate_fitness(current_best_schedule)

            if current_best_fitness > best_fitness:
                best_schedule = current_best_schedule
                best_fitness = current_best_fitness

            print(f"Generation {generation + 1} - Best Fitness: {best_fitness}")

        print("Best Fitness:", best_fitness)
        print("Best Schedule:")
        for activity in best_schedule:
            print(f"{activity.name}: Room - {activity.room.name}, Time - {activity.time}, Facilitator - {activity.facilitator.name}")

    with open("best_schedule.txt", "w") as file:
        for activity in best_schedule:
            file.write(f"{activity.name}: Room - {activity.room.name}, Time - {activity.time}, Facilitator - {activity.facilitator.name}\n")

    with open("best_schedule.csv", mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Activity Name", "Room Name", "Time Slot", "Facilitator Name"])
        for activity in best_schedule:
            writer.writerow([activity.name, activity.room.name, activity.time, activity.facilitator.name])