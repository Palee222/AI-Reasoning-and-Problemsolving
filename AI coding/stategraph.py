'''
my problem:
- Food-delivery robot
    - Correctly takes the right food to the right address on time and safely 
- Environment
    - Outside -> city
    - Inside the house or building
- robot
    - Can move in the environment
    - actuators: wheels, arms, sensors
    - Can detect obstacles and avoid them
    - alarm if it cannot reach the destination or if it gets stuck or if it gets damaged or if it is low on battery or if it is lost or if it is stolen or if it is hacked

'''

import networkx as nx
import matplotlib.pyplot as plt

def fooddelivery(food, time, address, robotposition):
    """
    Simulates a food delivery process.

    Parameters:
    food (str): The type of food being delivered.
    time (int): The estimated delivery time in minutes.
    address (str): The delivery address.
    robotposition (str): The robot's current position.

    Returns:
    str: A message confirming the delivery details.
    """
    if not food or not address or not robotposition:
        return "Error: Food and address must be provided."
    if robotposition != address:
        return "Error: Robot is not at the delivery address."

    return f"Your {food} will be delivered to {address} in approximately {time} minutes."
def delivery_robot_graph():
    return {
        "Idle": ["Order Received"],
        "Order Received": ["Moving To Restaurant", "Order Cancelled"],
        "Moving To Restaurant": ["At Restaurant", "Obstacle Detected"],
        "Obstacle Detected": ["Moving To Restaurant", "Needs Assistance"],
        "At Restaurant": ["Picking Up Food"],
        "Picking Up Food": ["Moving To Customer"],
        "Moving To Customer": ["At Customer", "Obstacle Detected"],
        "At Customer": ["Delivering Food"],
        "Delivering Food": ["Idle"],
        "Order Cancelled": ["Idle"],
        "Needs Assistance": ["Idle"],
    }
    
def statespacegraph():
    """
    Generates a state space graph for the food delivery process.

    Returns:
    dict: A representation of the state space graph.
    """
    return delivery_robot_graph()

def visualize_state_space(save_path=None):
    """Display the delivery robot graph and optionally save it as an image."""
    graph = nx.DiGraph(statespacegraph())
    positions = nx.spring_layout(graph, seed=7)

    terminal_states = {"Order Cancelled", "Needs Assistance"}
    node_colors = [
        "#9bd4c5" if state == "Idle"
        else "#f4c27a" if state in terminal_states
        else "#a9c7e8"
        for state in graph.nodes
    ]

    plt.figure(figsize=(13, 8))
    nx.draw_networkx(
        graph,
        positions,
        with_labels=True,
        node_color=node_colors,
        node_size=2800,
        font_size=9,
        font_weight="bold",
        arrows=True,
        arrowsize=20,
        edge_color="#5b6470",
        linewidths=1.5,
    )
    plt.title("Delivery Robot State-Space Graph")
    plt.axis("off")
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.show()

    return graph

def initial_robot_state():
    """Return the robot's state before it receives an order."""
    return {
        "robot_location": "warehouse",
        "order_status": "idle",
        "battery_level": 100,
        "carrying_food": False,
    }

def can_transition(current_state, next_state):
    """Return whether the graph allows a transition between two states."""
    return next_state in statespacegraph().get(current_state, [])

if __name__ == "__main__":
    visualize_state_space("delivery_robot_graph.png")