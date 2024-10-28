import pandas as pd
import ast
from collections import Counter

# Load the CSV file
df = pd.read_csv('topic_info_all.csv')

# Remove rows where 'Topic_' contains a '-'
df = df[~df['Topic_'].astype(str).str.contains('-')]

# Initialize a dictionary to keep track of used labels per TimePeriod
label_tracker = {}

# Define a function to select the best label based on word frequency in the list and ensuring uniqueness within the TimePeriod
def select_best_label(words, time_period, common_words):
    # Initialize the label tracker for the time period if it's not already there
    if time_period not in label_tracker:
        label_tracker[time_period] = set()
    
    # Choose the most frequent word from the common_words that exists in the 'words' list and hasn't been used
    for word, _ in common_words:
        if word in words and word not in label_tracker[time_period]:
            # Mark this word as used for this time period
            label_tracker[time_period].add(word)
            return word

    # If no common word fits, just return the first available word that hasn't been used
    for word in words:
        if word not in label_tracker[time_period]:
            label_tracker[time_period].add(word)
            return word
    
    # If all labels are used, return a unique generated label
    new_label = f"Label_{random.randint(1, 1000)}"
    label_tracker[time_period].add(new_label)
    return new_label

# Calculate common words across all KeyBERT lists for context fitting
all_keybert_words = []

# Convert KeyBERT strings into lists of words
for keybert_str in df['KeyBERT']:
    keyBERT_list = ast.literal_eval(keybert_str)  # Convert string to actual list
    all_keybert_words.extend(keyBERT_list)

# Count frequency of all words in KeyBERT lists
word_frequencies = Counter(all_keybert_words)

# Sort words by frequency to prioritize common words
common_words = word_frequencies.most_common()

# Create lists to hold the new labels, time periods, and bert allocations
labels = []
time_periods = []
bert_allocations = []

# Iterate through the DataFrame to assign the best-fitting label
for index, row in df.iterrows():
    keyBERT_list = ast.literal_eval(row['KeyBERT'])  # Convert string representation of list to actual list
    topic_ = row['Topic_']
    topic_parts = str(topic_).split('.')  # Split Topic_ by the decimal
    topic_prefix = topic_parts[0]  # Get the prefix before the decimal
    time_periods.append(topic_prefix)  # Add TimePeriod (before decimal)

    # Assign BertAllocation (after decimal)
    if len(topic_parts) > 1:
        bert_allocations.append(topic_parts[1])
    else:
        bert_allocations.append('0')  # Default to '0' if no allocation exists

    # Select the best label ensuring no repetition within the same time period
    label = select_best_label(keyBERT_list, topic_prefix, common_words)
    
    # Add the label to the labels list
    labels.append(label)

# Create the output DataFrame with KeyBERT, Topic_, Labels, TimePeriod, and BertAllocation
output_df = pd.DataFrame({
    'KeyBERT': df['KeyBERT'],
    'Topic_': df['Topic_'],
    'Label': labels,
    'TimePeriod': time_periods,
    'BertAllocation': bert_allocations
})

# Display the DataFrame in a Jupyter Notebook or standard Python environment
print(output_df)  # Use print to display in terminal or Jupyter notebook

# If you'd like to save the DataFrame to Excel:
output_df.to_excel('output_topic_info_test.xlsx', index=False)
