import csv
import sys

from util import Node, StackFrontier, QueueFrontier

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: first, last, activity
activities = {}


def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv") as file:
        reader = csv.DictReader(file)
        counter = 0
        for row in reader:
            # Increase counter
            counter += 1

            # Form name string
            name = row["first"] + " " + row["last"]
            people[counter] = {
                "name": name,
                "phone": row["phone"],
                "email": row["email"],
                "community": row["community"],
                "school": row["school"],
                "employer": row["employer"],
                "privacy": row["privacy"]
            }

            if name.lower() not in names:
                names[name.lower()] = {counter}
            else:
                names[name.lower()].add(counter)

    # Load activities
    with open(f"{directory}/activities.csv") as file:
        reader = csv.DictReader(file)
        counter = 0
        for row in reader:
            # Increase counter
            counter += 1

            # Form name string
            name = row["first"] + " " + row["last"]

            if name.lower() not in activities:
                activities[name.lower()] = {row["activity"]}
            else:
                activities[name.lower()].add(row["activity"])


def main():
    directory = "res"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = activities[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")


def shortest_path(source, target):
    """
    Returns the shortest list of (activity_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.
    """
    # Keep track of number of states explored
    num_explored = 0

    # Initialize frontier to just the starting position
    start = Node(state=source, parent=None, action=None)
    frontier = QueueFrontier()
    frontier.add(start)

    # Initialize an empty explored set
    explored = set()

    # If both person name is same, then no solution
    if source == target:
        return []

    # Keep looping until solution found
    while True:

        # If nothing left in frontier, then no path
        if frontier.empty():
            return None

        # Choose a node from the frontier
        node = frontier.remove()
        num_explored += 1

        # Mark node as explored
        explored.add(node.state)

        # Add neighbors to frontier
        for movie, state in neighbors_for_person(node.state):
            if not frontier.contains_state(state) and state not in explored:
                child = Node(state=state, parent=node, action=movie)

                # If node is the goal, then we have a solution
                if child.state == target:
                    node = child
                    path = []
                    while node.parent is not None:
                        path.append((node.action, node.state))
                        node = node.parent
                    path.reverse()
                    return path
                frontier.add(child)


def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            phone = person["phone"]
            email = person["email"]
            community = person["community"]
            school = person["school"]
            employer = person["employer"]
            privacy = person["privacy"]

            print(f"ID: {person_id}, Name: {name}, Phone: {phone}, Email: {email}, Community: {community}, "
                  f"School: {school}, Employer: {employer}, Privacy: {privacy}")
        try:
            person_id = int(input("Intended Person ID: "))
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id):
    """
    Returns (activities_id, person_id) pairs for people
    who starred with a given person.
    """
    privacy = people[person_id]["privacy"]
    if privacy == "Y":
        print("Privacy Requested")
        sys.exit(0)
    else:
        name = people[person_id]["first"] + " " + people[person_id]["last"]
        activities_ids = activities[name]["activity"]
        neighbors = set()
        for movie_id in activities_ids:
            for person_id in activities[movie_id]["stars"]:
                neighbors.add((movie_id, person_id))
        return neighbors


if __name__ == "__main__":
    main()
