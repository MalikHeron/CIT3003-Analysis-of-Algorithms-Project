class Queue:
    def __init__(self):
        self.array = []

    def contains_person(self, person):
        for node in self.array:
            if node.person == person:
                return True
        return False

    def empty(self):
        return len(self.array) == 0

    def enqueue(self, node):
        # add a node to the queue
        self.array.append(node)

    # Override remove function in Stack
    def dequeue(self):
        if self.empty():
            raise Exception("Queue empty")
        else:
            node = self.array[0]
            # remove first object and reassign array to new list
            self.array = self.array[1:]
            return node
