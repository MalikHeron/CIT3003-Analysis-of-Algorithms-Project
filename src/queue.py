class Queue:
    # Default constructor
    def __init__(self):
        self.array = []

    # For checking if a person is in the queue
    def contains_person(self, person):
        for node in self.array:
            if node.person == person:
                return True
        return False

    # For checking if queue is empty
    def is_empty(self):
        return len(self.array) == 0

    # For adding nodes to back of queue
    def enqueue(self, node):
        # add a node to the queue
        self.array.append(node)

    # For removing nodes from front of queue
    def dequeue(self):
        if self.is_empty():
            raise IndexError("Queue empty")
        else:
            node = self.array[0]
            # remove first object and reassign array to new list
            self.array = self.array[1:]
            return node
