import pandas as pd
import networkx as nx
import plotly.graph_objects as go
import webbrowser
import math

# Load the Excel file
file_path = 'topic_similarities.xlsx'
df = pd.read_excel(file_path, sheet_name='Sheet1')

# Load the Labelled_topics.csv for matching Topic_Labels
labelled_topics_path = 'Dashboard html\Labelled_topics.csv'
df_labels = pd.read_csv(labelled_topics_path)

# Initialize the graph
G = nx.DiGraph()

# Set initial source topic, similarity threshold, and distance increment for each time period
initial_source_topic = 2.5
similarity_threshold = 0.7
radius_increment = 1.5  # Distance increment for each time period

# Dictionary to store paths for DataFrame
paths_dict = {"source": [], "target_path": []}

# Function to get the Topic_Label from the labels CSV
def get_label(topic):
    label_row = df_labels[df_labels['Topic_'] == topic]
    return label_row['Topic_Label'].values[0] if not label_row.empty else f"Topic {topic}"

# Recursive function to add nodes and edges to the graph in radial layout and track paths
def add_nodes_and_edges(source_topic, source_time, level, path=[]):
    source_label = get_label(source_topic)
    source_node = f"{source_label} (Time {source_time})"
    path = path + [source_label]  # Track the path with labels only

    # Add path to the dictionary for DataFrame creation
    paths_dict["source"].append(source_label)
    paths_dict["target_path"].append(" -> ".join(path))  # Store path as string

    # Calculate radius for nodes of this time period level
    radius = radius_increment * level  # Distance from the initial source topic
    
    # Add source node if it does not already exist
    if source_node not in G:
        G.add_node(source_node, level=level, pos=(0, 0) if level == 1 else G.nodes[source_node]['pos'], color=color_map[source_time])
    
    # Find all targets one time period after the source time with similarity above the threshold
    target_df = df[(df['Source'] == source_topic) & (df['Target Time'] == source_time + 1) & (df['Value'] > similarity_threshold)]
    
    # Number of targets and angle increment to place them in a circle at the same radius
    num_targets = len(target_df)
    angle_increment = 2 * math.pi / max(1, num_targets)  # Avoid division by zero
    
    for i, (_, row) in enumerate(target_df.iterrows()):
        target_topic = row['Target']
        target_time = row['Target Time']
        angle_i = i * angle_increment  # Angle for this node in the circle
        
        # Calculate position for this target node at the determined radius
        x = radius * math.cos(angle_i)
        y = radius * math.sin(angle_i)
        target_label = get_label(target_topic)
        target_node = f"{target_label} (Time {target_time})"
        
        # Add the target node if not already present
        if target_node not in G:
            G.add_node(target_node, level=level + 1, pos=(x, y), color=color_map[target_time])
        
        # Add an edge from the source node to the target node
        G.add_edge(source_node, target_node, weight=row['Value'])
        
        # Recursive call to add the next level of nodes and edges
        add_nodes_and_edges(target_topic, target_time, level + 1, path=path)

# Assign colors by time period
unique_target_times = df['Target Time'].unique()
color_map = {time: f"hsl({(i * 360 / len(unique_target_times))}, 70%, 60%)" for i, time in enumerate(unique_target_times)}

# Start building the graph from the initial source topic and time 1
initial_source_time = df[df['Source'] == initial_source_topic]['Source Time'].iloc[0]
add_nodes_and_edges(initial_source_topic, initial_source_time, 1)

# Create the DataFrame from paths_dict with Topic_Labels
path_df = pd.DataFrame(paths_dict)
path_df.to_csv("source_target_paths.csv", index=False)
print("DataFrame with source topics and target paths saved as 'source_target_paths.csv'.")

# Prepare data for plotting with Plotly
node_x = []
node_y = []
node_color = []
node_hover_text = []
for node, data in G.nodes(data=True):
    x, y = data['pos']
    node_x.append(x)
    node_y.append(y)
    node_color.append(data['color'])
    
    # Use path data for hover text, handle cases where no matching path is found
    matching_path = path_df[path_df["source"] == node.split(' (Time')[0]]["target_path"]
    if not matching_path.empty:
        node_path = matching_path.values[0]
        node_hover_text.append(f"{node.split(' (Time')[0]}<br>Path: {node_path}")
    else:
        node_hover_text.append(f"{node.split(' (Time')[0]}<br>Path not found")  # Default message if path is missing

node_trace = go.Scatter(
    x=node_x, y=node_y,
    mode='markers',
    marker=dict(size=20, color=node_color),
    text=node_hover_text,
    hoverinfo='text',
    showlegend=False  # Hide nodes from legend
)

# Define traces for edges based on similarity level with thinner, smooth lines
edge_x_high, edge_y_high, edge_text_high = [], [], []
edge_x_med, edge_y_med, edge_text_med = [], [], []
edge_x_low, edge_y_low, edge_text_low = [], [], []

for edge in G.edges(data=True):
    x0, y0 = G.nodes[edge[0]]['pos']
    x1, y1 = G.nodes[edge[1]]['pos']
    similarity_value = edge[2]['weight']
    
    # Classify similarity into high, medium, and low
    if similarity_value > 0.85:
        edge_x_high += [x0, x1, None]
        edge_y_high += [y0, y1, None]
        edge_text_high.append(f"Similarity Value: {similarity_value:.2f}")
    elif similarity_value > 0.75:
        edge_x_med += [x0, x1, None]
        edge_y_med += [y0, y1, None]
        edge_text_med.append(f"Similarity Value: {similarity_value:.2f}")
    else:
        edge_x_low += [x0, x1, None]
        edge_y_low += [y0, y1, None]
        edge_text_low.append(f"Similarity Value: {similarity_value:.2f}")

edge_trace_high = go.Scatter(
    x=edge_x_high, y=edge_y_high, mode='lines',
    line=dict(width=0.5, color='black'),  # Thinner lines
    hoverinfo='text', text=edge_text_high, name="High Similarity"
)

edge_trace_med = go.Scatter(
    x=edge_x_med, y=edge_y_med, mode='lines',
    line=dict(width=0.5, color='grey'),  # Thinner lines
    hoverinfo='text', text=edge_text_med, name="Medium Similarity"
)

edge_trace_low = go.Scatter(
    x=edge_x_low, y=edge_y_low, mode='lines',
    line=dict(width=0.5, color='lightgrey'),  # Thinner lines
    hoverinfo='text', text=edge_text_low, name="Low Similarity"
)

# Add traces to the figure, with a legend for similarity and time period colors
fig = go.Figure(data=[edge_trace_high, edge_trace_med, edge_trace_low, node_trace],
                layout=go.Layout(
                    title='Related Topics by Time Period and Similarity',
                    title_x=0.5,
                    showlegend=True,
                    hovermode='closest',
                    hoverlabel=dict(font_size=10),
                    margin=dict(b=20, l=5, r=5, t=40),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                ))

# Add legend for time period colors
for time, color in color_map.items():
    fig.add_trace(go.Scatter(x=[None], y=[None], mode='markers',
                             marker=dict(size=10, color=color),
                             legendgroup=str(time), name=f"Time Period {time}"))

# Save the figure to an HTML file and open it immediately
html_file = "concentric_radial_spider_map_with_highlights.html"
fig.write_html(html_file)
webbrowser.open(html_file)

print("Concentric radial spider map with highlights generated and opened in the default browser.")
