import pandas as pd
import numpy as np
from Emotion_graph import generate_output_df
from bokeh.models import ColumnDataSource, HoverTool, CheckboxGroup, CustomJS, WMTSTileSource
from bokeh.plotting import figure, output_file, save
from bokeh.layouts import row
import os

# Get current working directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Generate the output_df by calling the function
output_df = generate_output_df()

# Load the geo information CSV file
doc_info_geo_file_path = os.path.join(current_dir, 'doc_info_geo.csv')
df_geo = pd.read_csv(doc_info_geo_file_path)

# Ensure the column names match for merging
df_geo.rename(columns={'Topic_': 'Topic_Column'}, inplace=True)

# Convert the 'Topic_' columns in both DataFrames to strings for matching
output_df['Topic_Column'] = output_df['Topic_Column'].astype(str)
df_geo['Topic_Column'] = df_geo['Topic_Column'].astype(str)

# Merge the output DataFrame with the geo information based on the topic
merged_df = pd.merge(output_df, df_geo[['Topic_Column', 'long', 'lat', 'name']],
                     left_on='Topic_Column', right_on='Topic_Column', how='inner')

# Convert lat/lon to Web Mercator for plotting (required by Bokeh maps)
def lat_lon_to_mercator(df):
    """Convert longitude and latitude to Web Mercator format."""
    k = 6378137  # WGS84 major axis in meters
    df['mercator_x'] = k * np.radians(df['long'])
    df['mercator_y'] = k * np.log(np.tan(np.pi / 4 + np.radians(df['lat']) / 2))
    return df

# Apply the coordinate transformation
merged_df = lat_lon_to_mercator(merged_df)

# Group by 'Topic_Column', 'TimePeriod', 'mercator_x', 'mercator_y', and 'name' to count occurrences
final_df = merged_df.groupby(['Topic_Column', 'TimePeriod', 'mercator_x', 'mercator_y', 'name']).size().reset_index(name='area_time_count')

# Size brackets (grouping counts into 4 size categories)
def assign_size_brackets(count):
    if count <= 10:
        return 8  # Small size
    elif count <= 50:
        return 12  # Medium size
    elif count <= 100:
        return 16  # Large size
    else:
        return 20  # Extra-large size

# Apply the size bracket logic to the data
final_df['size'] = final_df['area_time_count'].apply(assign_size_brackets)

# Get the unique time periods
time_periods = sorted(final_df['TimePeriod'].unique())

# Assign colors dynamically for time periods
colors = ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00', '#ffff33', '#a65628', '#f781bf']

# Map colors to time periods
final_df['color'] = final_df['TimePeriod'].apply(lambda tp: colors[time_periods.index(tp) % len(colors)])

# Create a separate ColumnDataSource for each time period
sources = {tp: ColumnDataSource(final_df[final_df['TimePeriod'] == tp]) for tp in time_periods}

# Prepare Bokeh plot
def make_plot():
    # Create a map plot
    p = figure(title="Locations of Topics", 
               x_axis_type="mercator", y_axis_type="mercator", 
               tools="pan,wheel_zoom,reset", 
               width=800, height=600)

    # Add tiles for OpenStreetMap using WMTSTileSource
    tile_source = WMTSTileSource(url="https://tile.openstreetmap.org/{z}/{x}/{y}.png")
    p.add_tile(tile_source)

    # Scatter plots for each time period with color and legend label
    renderers = []
    for tp in time_periods:
        renderer = p.scatter('mercator_x', 'mercator_y', size='size', color='color', 
                             source=sources[tp], fill_alpha=0.6, legend_label=str(tp), visible=True)
        renderers.append(renderer)

    # Add a hover tool that shows the topic count and city/town
    hover = HoverTool(tooltips=[
        ("Count", "@area_time_count"),
        ("City/Town", "@name")
    ])
    
    p.add_tools(hover)

    # Move the legend to the top-left and adjust properties
    p.legend.location = "top_left"
    p.legend.title = "Time Periods"
    p.legend.label_text_font_size = "10pt"
    p.legend.label_text_color = "black"

    return p, renderers

# Create initial plot and legend
plot, renderers = make_plot()

# Checkbox group for selecting time periods
checkbox_group = CheckboxGroup(labels=[str(tp) for tp in time_periods], active=list(range(len(time_periods))))

# Add callback to update visibility based on checkbox selection
checkbox_group.js_on_change('active', CustomJS(args=dict(renderers=renderers, time_periods=time_periods, checkboxes=checkbox_group), code="""
// Toggle visibility of scatter points for each time period
    const active_time_periods = checkboxes.active.map(i => parseInt(checkboxes.labels[i]));
    for (let i = 0; i < renderers.length; i++) {
        renderers[i].visible = active_time_periods.includes(time_periods[i]);
    }
"""))

# Arrange layout with the checkboxes next to the plot
layout = row(plot, checkbox_group)

# Save the plot to an HTML file in the same directory
output_file_path = os.path.join(current_dir, "geo_topics_plot.html")
output_file(output_file_path)  # Define the output file path

# Save the layout to the file
save(layout)

print(f"HTML file successfully generated: {output_file_path}")
