import pandas as pd
import networkx as nx
from bokeh.plotting import figure, output_file, show
from bokeh.models import Circle, HoverTool, MultiLine, ColumnDataSource, LinearColorMapper
from bokeh.io import output_notebook
from bokeh.palettes import Spectral8

# Load the data
df = pd.read_excel("topic_similarities.xlsx")

# Filter by similarity threshold (0.3)
threshold = 0.3
df_filtered = df[df['Value'] >= threshold]

# Initialize graph
G = nx.Graph()

# Add nodes and edges based on similarity and consecutive target time constraint
root_node = "1.0"  # Starting root node
G.add_node(root_node)

for i, row in df_filtered.iterrows():
    source, target, similarity = row['Source'], row['Target'], row['Value']
    source_time, target_time = row['Source Time'], row['Target Time']
    
    # Only add edges for consecutive target times
    if target_time == source_time + 1:
        G.add_node(target)
        # Calculate distance inversely proportional to similarity
        distance = 1 / similarity
        G.add_edge(source, target, weight=distance, similarity=similarity)

# Circular layout for the nodes
positions = nx.circular_layout(G)
node_x = [positions[node][0] for node in G.nodes()]
node_y = [positions[node][1] for node in G.nodes()]
node_names = list(G.nodes())

# Prepare edge data with line widths representing similarity
edge_start = []
edge_end = []
edge_widths = []
for start_node, end_node, data in G.edges(data=True):
    edge_start.append(positions[start_node])
    edge_end.append(positions[end_node])
    edge_widths.append(5 * (1 / data['similarity']))

# Bokeh plot setup
plot = figure(width=800, height=800, title="Spider Map Based on Similarity", tools="pan, wheel_zoom, save")

# Draw nodes
source = ColumnDataSource(data=dict(x=node_x, y=node_y, name=node_names))
plot.circle('x', 'y', size=10, fill_color="skyblue", source=source)

# Draw edges with varying line widths based on similarity
for start, end, width in zip(edge_start, edge_end, edge_widths):
    plot.line([start[0], end[0]], [start[1], end[1]], line_width=width, color="black")

# Hover tool for node names
hover = HoverTool(tooltips=[("Node", "@name")])
plot.add_tools(hover)

# Show the plot
output_notebook()
show(plot)
