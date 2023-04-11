from queue import Queue
import threading

class Node:
    def __init__(self, process_function):
        self.input_queue = Queue()
        self.output_queue = Queue()
        self.process_function = process_function

    def process(self):
        while True:
            data = self.input_queue.get()
            if data is None:
                break
            processed_data = self.process_function(data)
            self.output_queue.put(processed_data)

    def start(self):
        self.thread = threading.Thread(target=self.process)
        self.thread.start()

    def stop(self):
        self.input_queue.put(None)
        self.thread.join()

class Pipeline:
    def __init__(self, nodes):
        self.nodes = nodes
        self.input_queue = nodes[0].input_queue
        self.output_queue = nodes[-1].output_queue
        self.num_workers = 4

    def start(self):
        for node in self.nodes:
            node.start()

        workers = []
        for i in range(self.num_workers):
            worker = threading.Thread(target=self.worker_loop)
            worker.start()
            workers.append(worker)

        self.input_queue.join()

        for node in self.nodes:
            node.stop()

        for worker in workers:
            worker.join()

    def worker_loop(self):
        while True:
            data = self.input_queue.get()
            if data is None:
                self.input_queue.task_done()
                break
            for node in self.nodes:
                node.input_queue.put(data)
                data = node.output_queue.get()
            self.output_queue.put(data)
            self.input_queue.task_done()



def process_function_a(data):
    # Process data from previous node
    processed_data = data.upper()
    return processed_data


def process_function_b(data):
    # Process data from previous node
    processed_data = data[::-1]
    return processed_data


def process_function_c(data):
    # Process data from previous node
    processed_data = data.replace(' ', '-')
    return processed_data


if __name__ == '__main__':
    node_a = Node(process_function_a)
    node_b = Node(process_function_b)
    node_c = Node(process_function_c)

    pipeline = Pipeline([node_a, node_b, node_c])

    pipeline_thread = threading.Thread(target=pipeline.start)
    pipeline_thread.start()

    input_data = ['hello world', 'foo bar', 'spam eggs']

    for data in input_data:
        pipeline.input_queue.put(data)

    pipeline.input_queue.join()

    while not pipeline.output_queue.empty():
        output_data = pipeline.output_queue.get()
        print(output_data)

    pipeline_thread.join()
