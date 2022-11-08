import csv
import sys

from util import Node, StackFrontier, QueueFrontier

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps activities to a dictionary of: names
activities = {}


def load_data():
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open("res/people.csv") as file:
        reader = csv.DictReader(file)
        counter = 0
        for row in reader:
            # Increase counter
            counter += 1

            # Form name string
            name = row["first"] + " " + row["last"]

            # Add person details to people
            people[counter] = {
                "name": name,
                "phone": row["phone"],
                "email": row["email"],
                "community": row["community"],
                "school": row["school"],
                "employer": row["employer"],
                "privacy": row["privacy"]
            }

            # Check if name already exists
            if name.lower() not in names:
                names[name.lower()] = {counter}
            else:
                names[name.lower()].add(counter)

    # Load activities
    with open("res/activities.csv") as file:
        reader = csv.DictReader(file)
        counter = 0
        activity_counter = 0
        for row in reader:
            # Increase counter
            counter += 1

            # Form name string
            name = row["first"] + " " + row["last"]

            # Form list with name as key
            if name.lower() not in activities:
                activities[name.lower()] = {row["activity"]}
            else:
                activity = list(activities.get(name.lower(), set()))
                for index in activity:
                    if index != row["activity"]:
                        activities[name.lower()].add(row["activity"])
                    # else:
                    #    print(f"Duplicate: {row['activity']} at {name}")


def main():
    # Load data from files into memory
    print("Loading data...")
    load_data()
    print("Data loaded.")

    # Get name of source person
    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")

    # Get name of targeted person
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    # Get the path they are connected by
    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")

        # Add source number to path array
        path = [source] + path

        # Search and display how they are connected
        for i in range(degrees):
            person1 = people[path[i]]["name"]
            person2 = people[path[i + 1]]["name"]
            print(f"{i + 1}: {person1} is a close contact of {person2}")


def shortest_path(source, target):
    """
    Returns the shortest list of (person_id) that connects the source to the target.
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

    counter = 0

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

        counter += 1

        # Check if loop runs 6 times already
        if counter > 6:
            print(f"More than 6 degrees of separation")
            sys.exit(0)

        # Add neighbors to frontier
        for state in contacts_for_person(node.state):
            if not frontier.contains_state(state) and state not in explored:
                child = Node(state=state, parent=node, action=None)

                # If node is the goal, then we have a solution
                if child.state == target:
                    node = child
                    path = []
                    while node.parent is not None:
                        path.append(node.state)
                        node = node.parent
                    path.reverse()
                    return path
                frontier.add(child)


def person_id_for_name(name):
    """
    Returns the id for a person's name, resolving ambiguities as needed.
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


def contacts_for_person(person_id):
    """
    Returns (person_id) for people who are close contacts with a given person.
    """
    # Get source information
    source = people[person_id]
    source_community = source["community"]
    source_school = source["school"]
    source_employer = source["employer"]
    source_name = source["name"]
    source_privacy = source["privacy"]

    # Display source name
    print(f"Person: {source_name}")

    # Check if source requested privacy
    if source_privacy == "Y":
        print(f"No recommendations to close contacts, {source_name} requested privacy")

    contacts = set()
    have_activities = bool
    for index in names:
        person_ids = list(names.get(index, set()))
        for person_id in person_ids:
            person = people[person_id]
            contact_name = person["name"]
            contact_community = person["community"]
            contact_school = person["school"]
            contact_employer = person["employer"]
            contact_privacy = person["privacy"]

            if source_community == contact_community and source_school == contact_school \
                    or source_employer == contact_employer:
                # For storing recommendations
                recommendations = list()
                source_activities = list(activities.get(source_name.lower(), set()))
                # print(f"Source: {source_name}, Activities: {source_activities}")
                target_activities = list(activities.get(contact_name.lower(), set()))
                # print(f"Contact: {contact_name}, Activities: {target_activities}")

                if source_privacy != "Y":
                    if contact_privacy != "Y":
                        # Check if source has activities
                        if source_activities:
                            for activity in source_activities:
                                if activity not in target_activities:
                                    if activity not in recommendations:
                                        recommendations.append(f"{source_name} {activity}")
                            # Check for recommendations
                            if recommendations:
                                print(f"Recommendations to {contact_name}: {recommendations}")
                        else:
                            have_activities = False
                contacts.add(person_id)
    if not have_activities:
        print(f"{source_name} has no activities")
    return contacts


if __name__ == "__main__":
    main()
