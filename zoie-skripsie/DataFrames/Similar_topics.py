import pandas as pd
from bokeh.plotting import figure, show, output_file
from bokeh.models import HoverTool, ColumnDataSource

# Load necessary data as per existing data processing script
# Load the Excel file with topic similarities
similarities_file_path = 'topic_similarities.xlsx'  # Replace with actual file path
df_similarities = pd.read_excel(similarities_file_path)

# Load the CSV file with topic info and counts
topic_info_file_path = 'topic_info_all.csv'  # Replace with actual file path
df_topic_info = pd.read_csv(topic_info_file_path)

# Filter and process data as per logic in original script
# Ensure 'Value' column in similarities file is numeric and filter by value > 0.7 and Source == 1.0
df_similarities['Value'] = pd.to_numeric(df_similarities['Value'], errors='coerce')
filtered_df = df_similarities[(df_similarities['Value'] > 0.7) & (df_similarities['Source'] == 1.0)]

# Pick row with highest similarity for each Source and Target Time
filtered_df = filtered_df.loc[filtered_df.groupby(['Source', 'Target Time'])['Value'].idxmax()]

# Prepare output DataFrame for plotting
output_df = pd.DataFrame({
    'Topic_Column': filtered_df['Target'],
    'TimePeriod': filtered_df['Target Time']
})

# Ensure correct merging with topic counts and select necessary columns for plotting
df_topic_info['Topic_'] = df_topic_info['Topic_'].astype(str)
output_df['Topic_Column'] = output_df['Topic_Column'].astype(str)
output_df = pd.merge(output_df, df_topic_info[['Topic_', 'Count']], 
                     left_on='Topic_Column', right_on='Topic_', how='left')
output_df.drop(columns=['Topic_'], inplace=True)

# Prepare data for the line graph
x = output_df['TimePeriod'].astype(int)  
y = output_df['Count'].astype(int)       
source = ColumnDataSource(data=dict(
    x=x,
    y=y
))

# Output file for the plot
output_file("tweets_over_time.html")

# Create the plot
p = figure(title="Tweets over Time", x_axis_label="Time Period", y_axis_label="Count",
           width=800, height=400)

# Add line and circle for data points
p.line('x', 'y', source=source, line_width=2, color="navy", legend_label="Count")
p.circle('x', 'y', size=8, color="navy", alpha=0.5, source=source)

# Add HoverTool to display Time Period and Count on hover
hover = HoverTool()
hover.tooltips = [("Time Period", "@x"), ("Count", "@y")]
p.add_tools(hover)

# Show the plot
show(p)
