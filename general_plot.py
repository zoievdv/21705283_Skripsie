import os
import pandas as pd
from bokeh.plotting import figure, output_file, save
from bokeh.models import HoverTool, ColumnDataSource

# Get the directory of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Load your specific files
similarities_file_path = os.path.join(current_dir, 'topic_similarities.xlsx')
topic_info_file_path = os.path.join(current_dir, 'topic_info_all.csv')

# Ensure the input files exist
if not os.path.exists(similarities_file_path):
    raise FileNotFoundError(f"File not found: {similarities_file_path}")
if not os.path.exists(topic_info_file_path):
    raise FileNotFoundError(f"File not found: {topic_info_file_path}")

# Load and process data
df_similarities = pd.read_excel(similarities_file_path)
df_topic_info = pd.read_csv(topic_info_file_path)

df_similarities['Value'] = pd.to_numeric(df_similarities['Value'], errors='coerce')
filtered_df = df_similarities[(df_similarities['Value'] > 0.7) & (df_similarities['Source'] == 1.2)]
filtered_df = filtered_df.loc[filtered_df.groupby(['Source', 'Target Time'])['Value'].idxmax()]

output_df = pd.DataFrame({
    'Topic_Column': filtered_df['Target'],
    'TimePeriod': filtered_df['Target Time']
})

df_topic_info['Topic_'] = df_topic_info['Topic_'].astype(str)
output_df['Topic_Column'] = output_df['Topic_Column'].astype(str)

output_df = pd.merge(output_df, df_topic_info[['Topic_', 'Count']],
                     left_on='Topic_Column', right_on='Topic_', how='left')
output_df.drop(columns=['Topic_'], inplace=True)

time_period = output_df['TimePeriod'].astype(int)
count = output_df['Count'].astype(int)

# Create the plot with responsive sizing
source = ColumnDataSource(data=dict(x=time_period, y=count))
p = figure(
    title="Topic Counts over Time Period",
    x_axis_label='Time Period',
    y_axis_label='Topic Count',
    sizing_mode="stretch_both"  # Responsive sizing
)
p.line('x', 'y', source=source, line_width=2, color="#33a02c", legend_label="Count")
p.scatter('x', 'y', size=8, color="#33a02c", source=source, legend_label="Count")
p.add_tools(HoverTool(tooltips=[("Time Period", "@x"), ("Count", "@y")]))  # Add hover functionality

# Output the plot to an HTML file in the same directory
output_file_path = os.path.join(current_dir, "general_plot_line.html")
output_file(output_file_path)

# Save the plot
save(p)

# Print confirmation
print(f"Plot successfully saved to: {output_file_path}")
