import pandas as pd
from bokeh.plotting import figure, show, output_file
from bokeh.models import HoverTool, CheckboxGroup, CustomJS
from bokeh.io import output_notebook
from bokeh.layouts import column
from bokeh.models import ColumnDataSource

# Load the Excel file with topic similarities
similarities_file_path = 'topic_similarities.xlsx'  # Replace with your actual file path
df_similarities = pd.read_excel(similarities_file_path)

# Load the CSV file with topic info and counts
topic_info_file_path = 'topic_info_all.csv'  # Replace with your actual file path
df_topic_info = pd.read_csv(topic_info_file_path)

# Load the CSV file with sentiment information, skipping bad lines
doc_info_sentiment_file_path = 'doc_info_sentiment.csv'  # Replace with your actual file path
df_sentiment = pd.read_csv(doc_info_sentiment_file_path, on_bad_lines='skip', low_memory=False)

# Load the CSV file with user verification information
doc_info_use_file_path = 'doc_info_use.csv'  # Replace with your actual file path
df_use = pd.read_csv(doc_info_use_file_path)

# Ensure numeric columns ('pos', 'neu', 'neg') are converted properly
df_sentiment['pos'] = pd.to_numeric(df_sentiment['pos'], errors='coerce')
df_sentiment['neu'] = pd.to_numeric(df_sentiment['neu'], errors='coerce')
df_sentiment['neg'] = pd.to_numeric(df_sentiment['neg'], errors='coerce')

# Drop rows where any sentiment value is NaN (due to improper data)
df_sentiment = df_sentiment.dropna(subset=['pos', 'neu', 'neg'])

# Ensure 'Value' column is numeric in similarities file
df_similarities['Value'] = pd.to_numeric(df_similarities['Value'], errors='coerce')

# Filter rows where 'Value' is greater than 0.7 and 'Source' equals 1.0
filtered_df = df_similarities[(df_similarities['Value'] > 0.7) & (df_similarities['Source'] == 1.0)]

# For each Source and Target Time, pick the row with the highest similarity (Value)
filtered_df = filtered_df.loc[filtered_df.groupby(['Source', 'Target Time'])['Value'].idxmax()]

# Create new columns: Topic_Column (Target Topic) and TimePeriod (Target Time)
output_df = pd.DataFrame({
    'Topic_Column': filtered_df['Target'],  # This will contain all Target topics
    'TimePeriod': filtered_df['Target Time']  # Time period corresponding to the Target topic
})

# Convert 'Target' from similarities to match the 'Topic_' in the topic_info CSV
df_topic_info['Topic_'] = df_topic_info['Topic_'].astype(str)
output_df['Topic_Column'] = output_df['Topic_Column'].astype(str)

# Merge the Count from topic_info_all.csv based on matching 'Topic_' from df_topic_info with 'Topic_Column' from output_df
output_df = pd.merge(output_df, df_topic_info[['Topic_', 'Count']], 
                     left_on='Topic_Column', right_on='Topic_', how='left')

# Drop the extra 'Topic_' column from the merge
output_df.drop(columns=['Topic_'], inplace=True)

# Ensure 'Topic_' in the sentiment data matches the format of 'Topic_Column'
df_sentiment['Topic_'] = df_sentiment['Topic_'].astype(str)

# Define a function to calculate average sentiment values and multiply them by the Count
def calculate_weighted_sentiment(topic_column, count, sentiment_df):
    matching_rows = sentiment_df[sentiment_df['Topic_'] == topic_column]
    
    avg_pos = matching_rows['pos'].mean() if not matching_rows.empty else 0
    avg_neu = matching_rows['neu'].mean() if not matching_rows.empty else 0
    avg_neg = matching_rows['neg'].mean() if not matching_rows.empty else 0
    
    positive_value = avg_pos * count
    neutral_value = avg_neu * count
    negative_value = avg_neg * count
    
    return positive_value, neutral_value, negative_value

# Initialize empty lists to hold sentiment calculations
positive_values = []
neutral_values = []
negative_values = []

# Iterate through the output_df and calculate sentiment for each row
for index, row in output_df.iterrows():
    positive, neutral, negative = calculate_weighted_sentiment(row['Topic_Column'], row['Count'], df_sentiment)
    positive_values.append(positive)
    neutral_values.append(neutral)
    negative_values.append(negative)

# Add the calculated sentiment values to the output DataFrame
output_df['Positive'] = positive_values
output_df['Neutral'] = neutral_values
output_df['Negative'] = negative_values

# Round sentiment columns to the nearest integer
output_df['Positive'] = output_df['Positive'].round(0).astype(int)
output_df['Neutral'] = output_df['Neutral'].round(0).astype(int)
output_df['Negative'] = output_df['Negative'].round(0).astype(int)

# Add % Verified User Tweets column
def calculate_verified_percentage(topic_column, count, use_df):
    matching_rows = use_df[(use_df['Topic_'] == topic_column) & (use_df['verified'] == True)]
    
    verified_count = len(matching_rows)
    percentage_verified = (verified_count / count) * 100 if count > 0 else 0
    
    return percentage_verified

# Initialize the list for % Verified User Tweets
verified_percentages = []

# Iterate through the output_df to calculate the percentage of verified tweets for each topic
for index, row in output_df.iterrows():
    verified_percentage = calculate_verified_percentage(row['Topic_Column'], row['Count'], df_use)
    verified_percentages.append(verified_percentage)

# Add the calculated percentages to the output DataFrame
output_df['% Verified User Tweets'] = verified_percentages

# Prepare data for the Bokeh plot
x = output_df['TimePeriod'].astype(int)  
y = output_df['Count'].astype(int)       

# Scale dot sizes: The largest % Verified User Tweets should be 3x the base size
base_size = 10
max_verified = output_df['% Verified User Tweets'].max()
output_df['dot_size'] = (output_df['% Verified User Tweets'] / max_verified) * (3 * base_size)

# Create a ColumnDataSource to allow tooltips
source = ColumnDataSource(data=dict(x=x, y=y, size=output_df['dot_size'], 
                                    verified=output_df['% Verified User Tweets'], 
                                    pos=output_df['Positive'], 
                                    neu=output_df['Neutral'], 
                                    neg=output_df['Negative']))

# Create the Bokeh plot
output_notebook()  
output_file("topic_counts_over_time.html")  

# Define colors
line_color = "#1f78b4"  
neg_color = "#e31a1c"  
neu_color = "#ffcc00"  
pos_color = "#33a02c"  

p = figure(title="Topic Counts over Time Period", 
           x_axis_label='Time Period', 
           y_axis_label='Topic Count',
           width=800, height=400)

# Create the main line plot
p.line('x', 'y', source=source, line_width=2, color=line_color, legend_label="Count")

# Create scatter for topic counts, with size based on % Verified User Tweets
p.scatter('x', 'y', size='size', color=line_color, legend_label="Count", source=source)

# Add scatter points for Negative, Neutral, and Positive lines, initially hidden
neg_scatter = p.scatter('x', 'neg', size=6, color=neg_color, source=source, legend_label="Negative", visible=False)
neu_scatter = p.scatter('x', 'neu', size=6, color=neu_color, source=source, legend_label="Neutral", visible=False)
pos_scatter = p.scatter('x', 'pos', size=6, color=pos_color, source=source, legend_label="Positive", visible=False)

# Add lines for Negative, Neutral, and Positive sentiment, initially hidden
negative_line = p.line('x', 'neg', source=source, line_width=2, color=neg_color, legend_label="Negative", visible=False)
neutral_line = p.line('x', 'neu', source=source, line_width=2, color=neu_color, legend_label="Neutral", visible=False)
positive_line = p.line('x', 'pos', source=source, line_width=2, color=pos_color, legend_label="Positive", visible=False)

# Add HoverTool to display the count, % Verified User Tweets, and sentiment values on hover
hover = HoverTool()
hover.tooltips = [("Time Period", "@x"), ("Count", "@y"), ("% Verified", "@verified%"), 
                  ("Positive", "@pos"), ("Neutral", "@neu"), ("Negative", "@neg")]
p.add_tools(hover)

# Create checkboxes to control visibility of sentiment lines and scatter points
checkbox = CheckboxGroup(labels=["Show Negative", "Show Neutral", "Show Positive"], active=[])

# Define a CustomJS callback to show/hide lines and scatter points based on checkbox state
callback = CustomJS(args=dict(neg_line=negative_line, neg_scatter=neg_scatter, neu_line=neutral_line, neu_scatter=neu_scatter, pos_line=positive_line, pos_scatter=pos_scatter, checkbox=checkbox), code="""
    neg_line.visible = checkbox.active.includes(0);
    neg_scatter.visible = checkbox.active.includes(0);
    
    neu_line.visible = checkbox.active.includes(1);
    neu_scatter.visible = checkbox.active.includes(1);
    
    pos_line.visible = checkbox.active.includes(2);
    pos_scatter.visible = checkbox.active.includes(2);
""")

# Similar_topics.py

def generate_output_df():
    # Your logic that generates output_df
    # Return the final DataFrame
    return output_df


# Link the checkbox to the callback
checkbox.js_on_change('active', callback)

# Layout the plot and checkbox
layout = column(p, checkbox)

# Show the plot with the checkboxes
show(layout)