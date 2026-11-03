import matplotlib.pyplot as plt
import os

# Data for the comparison table
columns = ('Feature', 'Previous Studies', 'Proposed System (This Project)')
data = [
    ['Linguistic Scope', 'Often 10-15 signs', 'Full 28-Letter Arabic Alphabet'],
    ['Hardware', 'Desktop PC / High-end GPU', 'Raspberry Pi 4 (Portable Edge AI)'],
    ['Inference Speed', 'Slow or Offline (Batch)', 'Real-time (24-30 FPS)'],
    ['User Interface', 'Basic Command Line / Script', 'Modern Web UI (Flask/Glassmorphism)'],
    ['Audio Feedback', 'Mostly Not Available', 'Integrated (Microsoft Edge-TTS)']
]

# Set up the plot
fig, ax = plt.subplots(figsize=(10, 3.5))
ax.axis('tight')
ax.axis('off')

# Create the table
table = ax.table(cellText=data, colLabels=columns, cellLoc='center', loc='center')

# Polish the table styles
table.auto_set_font_size(False)
table.set_fontsize(11)
table.scale(1.2, 2.0) # Scale it for better legibility

# Color header
for (row, col), cell in table.get_celld().items():
    if row == 0:
        cell.set_text_props(weight='bold', color='white')
        cell.set_facecolor('#1f77b4') # Nice professional blue
    elif col == 2:
        cell.set_text_props(weight='bold', color='#1f77b4') # Highlight project column

# Save the table
output_dir = r"c:\Users\mohammed\ProjectStart\صوره"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

file_path = os.path.join(output_dir, 'comparison_table.png')
plt.savefig(file_path, dpi=300, bbox_inches='tight', transparent=False)
print(f"Success: Comparison table saved at {file_path}")
