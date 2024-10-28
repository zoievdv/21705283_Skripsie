import pandas as pd
from bokeh.plotting import figure, show, output_file
from bokeh.models import HoverTool, ColumnDataSource

# Load or create your data for Time Periods and Counts
data = {
    'TimePeriod': [1, 2, 3, 4, 5],  # Replace with your actual time periods
    'Count': [120, 230, 180, 320, 260]  # Replace with your actual counts
}
output_df = pd.DataFrame(data)

# Set up ColumnDataSource for Bokeh
source = ColumnDataSource(data=dict(
    x=output_df['TimePeriod'],
    y=output_df['Count']
))

# Define output file
output_file("tweets_over_time.html")

# Create the plot
p = figure(title="Tweets over Time", x_axis_label="Time Period", y_axis_label="Count",
           width=800, height=400)

# Plot the line graph with circles on data points
p.line('x', 'y', source=source, line_width=2, color="navy", legend_label="Count")
p.circle('x', 'y', size=8, color="navy", alpha=0.5, source=source)

# Add HoverTool to show Time Period and Count on hover
hover = HoverTool()
hover.tooltips = [("Time Period", "@x"), ("Count", "@y")]
p.add_tools(hover)

# Show the plot
show(p)
