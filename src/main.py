import csv
import sys

from math import log
from queue import Queue
from node import Node

""" Sources: 
    https://github.com/priyanktejani/degrees
    https://github.com/alireza-mahmoodi/Six_Degrees_of_Kevin_Bacon.git 
"""

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, phone, email, community, school, employer, privacy
people = {}

# Maps names to a dictionary of: activities
activities = {}


def load_data():
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open("../res/people.csv") as file:
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
    with open("../res/activities.csv") as file:
        reader = csv.DictReader(file)
        counter = 0
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
    print("Data loaded.\n")

    # Get name of source person
    source = get_person_id(input("Name: "))
    if source is None:
        sys.exit("Person not found.")

    # Get name of targeted person
    target = get_person_id(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    # Get the path and average of the connection
    result = find_connection(source, target)
    try:
        # Get path value
        path = result[0]
        # Get average value
        average = round(result[1], 3)
    except TypeError:
        path = None
        average = 0

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        if degrees == 1:
            print(f"\n{degrees} degree of separation.")
        elif degrees > 1:
            print(f"\n{degrees} degrees of separation.")

        # Add source number to path array
        path = [source] + path

        # Search and display how they are connected
        for i in range(degrees):
            person1 = people[path[i]]["name"]
            person2 = people[path[i + 1]]["name"]
            print(f"{i + 1}: {person1} is a close contact of {person2}")

        print(f"\nAverage degrees of separation: {average}")


def find_connection(source, target):
    """ Returns the list of (person_id) that connects the source to the target.
    If not possible path, returns None. """

    # If both persons' name is the same, then exit program
    if source == target:
        sys.exit("Same person")

    # Initialize node
    node = Node(person=source, parent=None)
    # Create object of Queue
    queue = Queue()
    # Add node to queue
    queue.enqueue(node)
    # Keeping track of the number of similar contacts
    similar_contacts = 0
    # For storing sum of averages
    total_average = 0.0

    # For storing checked persons
    checked = set()

    # Keep looping until a solution is found
    while True:

        # If queue is empty then no path exists
        if queue.is_empty():
            return None

        # Get next node from the queue
        current_node = queue.dequeue()
        # Reset child count on loop
        child_count = 0
        # Get current person name
        source = people[current_node.person]
        source_name = source["name"]

        # Check close contacts for the current node
        for current_person in get_close_contacts(current_node.person, target):
            # Check if the current person exists in the set
            if not queue.contains_person(current_person) and current_node.person not in checked:
                # Create a new node on tree
                child = Node(person=current_person, parent=current_node)
                child_count += 1
                # If the person in the current node matches the target, then find and return path
                if child.person == target:
                    node = child
                    # print(f"Parent: {node.parent}")
                    path = []
                    while node.parent is not None:
                        # Add person to the path
                        path.append(node.person)
                        # print(f"Path: {path}")
                        # Set node to parent node
                        node = node.parent
                        # print(f"Parent: {node.parent}")
                    path.reverse()
                    # print(f"Path reversed: {path}")
                    try:
                        # Calculate final average
                        final_average = total_average / len(checked)
                        return path, final_average
                    except ZeroDivisionError:
                        return path, 1

                # Add child node to queue
                queue.enqueue(child)
            else:
                similar_contacts += 1

        # Add current node to checked list
        checked.add(current_node.person)
        try:
            # Calculate average separation
            average = log(len(people)) / log(child_count)
        except ValueError:
            average = 0
        except ZeroDivisionError:
            average = 0
        # Total average separation
        total_average += average
        # print(f"Close contacts: {child_count}")
        # print(f"Similar contacts: {similar_contacts}")
        # print(f"Average separation: {average}")
        # print(f"Checked: {source_name}")


def get_person_id(name):
    """ Returns the id for a person's name, avoiding any ambiguities. """
    # Get list of ids for particular name
    person_ids = list(names.get(name.lower(), set()))

    # Check if list is empty
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"\nWhich '{name}'?")
        for person_id in person_ids:
            # Get person information
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

        # Give user 3 tries to enter correct data type
        for tries in range(0, 3):
            try:
                person_id = int(input("\nIntended Person ID: "))
                # Check if entered id is valid
                if person_id in person_ids:
                    return person_id
                return None
            except ValueError:
                print(f"Integer value expected. Tries remaining {2 - tries}")
                continue
        # User has entered invalid inputs to reach this point
        sys.exit("\nInvalid inputs!")
    else:
        return person_ids[0]


def get_close_contacts(source_id, target_id):
    """ Returns (person_id) for people who are close contacts with a given person. """
    # Get source information
    source = people[source_id]
    source_community = source["community"]
    source_school = source["school"]
    source_employer = source["employer"]
    source_name = source["name"]

    # Display source name
    print(f"\nChecking close contacts for: [{source_id}] {source_name}")

    # Storing close contacts
    close_contacts = set()
    # Storing whether source has activities
    have_activities = bool

    # Iterate through names
    for name in names:
        # Get list of ids for particular name
        person_ids = list(names.get(name, set()))

        # Iterate through ids
        for person_id in person_ids:
            # Get contact information
            person = people[person_id]
            contact_name = person["name"]
            contact_community = person["community"]
            contact_school = person["school"]
            contact_employer = person["employer"]
            contact_privacy = person["privacy"]

            # Check if contact is a close contact
            if source_community == contact_community or source_school == contact_school \
                    or source_employer == contact_employer:
                # Check if target person is the current close contact
                if people[target_id] == person:
                    # Add current close contact and stop searching
                    close_contacts.add(person_id)
                    return close_contacts

                # For storing recommendations
                recommendations = list()
                # Activities source does
                source_activities = list(activities.get(source_name.lower(), set()))
                # Activities target does
                target_activities = list(activities.get(contact_name.lower(), set()))

                # Check if contact requested privacy
                if contact_privacy != "Y":
                    # Check if source has activities
                    if source_activities:
                        # Iterate through source activities
                        for activity in source_activities:
                            # Check if source activities are in target activities
                            if activity not in target_activities:
                                # Check if activity is already in recommendation list
                                if activity not in recommendations:
                                    # Add activity to recommendations
                                    recommendations.append(f"{source_name} {activity}")
                        # Check for recommendations
                        if recommendations:
                            print(f"Recommendations sent to [{person_id}] {contact_name}: {recommendations}")
                    else:
                        # Source has no activities
                        have_activities = False
                else:
                    print(f"No recommendations sent to [{person_id}] {contact_name}, privacy requested")
                # Add contact to close contacts
                close_contacts.add(person_id)
    if not have_activities:
        print(f"[{source_id}] {source_name} has no activities")
    return close_contacts


if __name__ == "__main__":
    main()
