import pandas as pd
import numpy as np
from Emotion_graph import generate_output_df
from bokeh.models import ColumnDataSource, HoverTool, CheckboxGroup, CustomJS, Legend, LegendItem
from bokeh.plotting import figure, output_file, save
from bokeh.layouts import column, row
from bokeh.palettes import Oranges256, Greens256, linear_palette
from bokeh.tile_providers import Vendors

# Generate the output_df by calling the function
output_df = generate_output_df()

# Load the geo information CSV file
doc_info_geo_file_path = 'doc_info_geo.csv'  # Replace with your actual path
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
    df['mercator_x'] = df['long'] * (20037508.34 / 180.0)
    df['mercator_y'] = np.log(np.tan((90 + df['lat']) * np.pi / 360.0)) * (20037508.34 / np.pi)
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

# Dynamically generate enough dark to medium shades of orange or green
palette_orange = linear_palette(Oranges256[50:150], len(time_periods))  # Darker shades of orange
palette_green = linear_palette(Greens256[50:150], len(time_periods))    # Darker shades of green

# Alternate between orange and green for variety
colors = [palette_orange[i % len(palette_orange)] if i % 2 == 0 else palette_green[i % len(palette_green)] for i in range(len(time_periods))]

# Add color to the dataframe by mapping time periods to different colors
final_df['color'] = final_df['TimePeriod'].apply(lambda tp: colors[time_periods.index(tp)])

# Create a separate ColumnDataSource for each time period
sources = {tp: ColumnDataSource(final_df[final_df['TimePeriod'] == tp]) for tp in time_periods}

# Prepare Bokeh plot
def make_plot():
    # Create a map plot with light grey tiles
    p = figure(title="Locations of Topics", 
               x_axis_type="mercator", y_axis_type="mercator", 
               x_axis_label='Longitude', 
               y_axis_label='Latitude',
               tools="pan,wheel_zoom,reset", width=800, height=600)

    # Add the tile provider directly using add_tile
    p.add_tile(Vendors.CARTODBPOSITRON)

    # Scatter plots for each time period with color and legend label
    renderers = []
    for tp in time_periods:
        renderer = p.scatter('mercator_x', 'mercator_y', size='size', color='color', 
                             source=sources[tp], fill_alpha=0.6, legend_label=str(tp), visible=True)
        renderers.append(renderer)

    # Add a hover tool that shows only the topic count and city/town
    hover = HoverTool(tooltips=[
        ("Count", "@area_time_count"),
        ("City/Town", "@name")
    ])
    
    p.add_tools(hover)

    # Move the legend to the right and adjust properties
    p.legend.location = "top_left"
    p.legend.title = "Time Periods"
    p.legend.label_text_font_size = "10pt"
    p.legend.label_text_color = "black"

    return p, renderers

# Function to toggle visibility based on selected checkboxes
def update_visibility(active_time_periods):
    for i, renderer in enumerate(renderers):
        renderer.visible = (time_periods[i] in active_time_periods)

# Create initial plot and legend
plot, renderers = make_plot()

# Checkbox group for selecting time periods
checkbox_group = CheckboxGroup(labels=[str(tp) for tp in time_periods], active=list(range(len(time_periods))))

# Add callback to update visibility based on checkbox selection
checkbox_group.js_on_change('active', CustomJS(args=dict(renderers=renderers, time_periods=time_periods, checkboxes=checkbox_group), code="""
    const active_time_periods = checkboxes.active.map(i => parseInt(checkboxes.labels[i]));
    
    // Toggle visibility based on active checkboxes
    for (let i = 0; i < renderers.length; i++) {
        renderers[i].visible = active_time_periods.includes(time_periods[i]);
    }
"""))

# Arrange layout with the checkboxes on the right of the plot
layout = row(plot, checkbox_group)

# Save the plot to an HTML file
output_file("geo_topics_plot.html")  # This defines the output file

# Save the layout to the file
save(layout)

print("HTML file successfully generated: geo_topics_plot.html")
