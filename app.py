from flask import Flask, render_template, request
import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

graph = None

def get_node_names(graph):
    node_ids = list(graph.nodes())
    return node_ids
def get_map_data(city_name):
    place_name = city_name + ", Algeria"
    try:
        graph = ox.graph_from_place(place_name, network_type='drive')
        return graph
    except Exception as e:
        print(f"Error fetching map data for {place_name}: {e}")
        return None

def plot_shortest_path(graph, shortest_path):
    fig, ax = ox.plot_graph_route(graph, shortest_path, route_color='yellow', route_linewidth=3, node_size=0, figsize=(15, 15), show=False, close=False)
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    return plot_url

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/select_city', methods=['GET', 'POST'])
def select_city():
    global graph
    if request.method == 'POST':
        selected_city = request.form['city']
        graph = get_map_data(selected_city)
        if graph is None:
            return render_template('error.html', message=f"Error fetching map data for {selected_city}")
        
        # Get node IDs from the graph
        node_ids = get_node_names(graph)
        
        return render_template('shortest_path.html', node_ids=node_ids)

    cities = ["Adrar", "Ain Defla", "Bejaia"]  # List of city names
    return render_template('select_city.html', cities=cities)

@app.route('/shortest_path', methods=['POST'])
def shortest_path():
    global graph
    if graph is None:
        return render_template('error.html', message="Graph data not available. Please select a city first.")

    selected_source = int(request.form['source'])
    selected_target = int(request.form['target'])

    # Check if the selected source and target nodes exist in the graph
    if selected_source not in graph.nodes or selected_target not in graph.nodes:
        return render_template('error.html', message="Selected source or target node does not exist in the graph.")

    # Find the shortest path between selected source and target nodes using A*
    try:
        shortest_path = nx.astar_path(graph, selected_source, selected_target, weight='length')
    except nx.NetworkXNoPath:
        return render_template('error.html', message="No path found between selected source and target nodes.")

    plot_url = plot_shortest_path(graph, shortest_path)

    return render_template('shortest_path_result.html', shortest_path=shortest_path, plot_url=plot_url)

if __name__ == '__main__':
    app.run(debug=True)