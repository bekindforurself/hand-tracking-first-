import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

# Set up the plot
fig, ax = plt.subplots(figsize=(12, 10))
ax.set_xlim(0, 10)
ax.set_ylim(0, 12)
ax.axis('off')

# Helper function to draw boxes
def draw_box(x, y, text, box_style='round', color='#1f77b4', width=2.5, height=0.8):
    box = patches.FancyBboxPatch((x-width/2, y-height/2), width, height, 
                                 boxstyle=box_style, linewidth=2, edgecolor=color, facecolor='white')
    ax.add_patch(box)
    ax.text(x, y, text, ha='center', va='center', fontsize=11, fontweight='bold', wrap=True)

# Helper function to draw decision diamonds
def draw_diamond(x, y, text, color='#d62728', width=2.5, height=1.0):
    diamond_coords = [[x, y+height/2], [x+width/2, y], [x, y-height/2], [x-width/2, y]]
    diamond = patches.Polygon(diamond_coords, linewidth=2, edgecolor=color, facecolor='white')
    ax.add_patch(diamond)
    ax.text(x, y, text, ha='center', va='center', fontsize=10, fontweight='bold', wrap=True)

# Helper function for arrows
def draw_arrow(x1, y1, x2, y2):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', lw=1.5, color='black'))

# Drawing the Flowchart elements
draw_box(5, 11, "START\nSystem Initialize", box_style='round,pad=0.1', color='green')
draw_arrow(5, 10.6, 5, 10.2)

draw_box(5, 9.8, "Input Capture\n(Webcam / OpenCV)", color='#1f77b4')
draw_arrow(5, 9.4, 5, 9.0)

draw_diamond(5, 8.3, "Hand Detected?")
draw_arrow(5, 7.8, 5, 7.4) # Yes
draw_arrow(3.75, 8.3, 3, 8.3) # No path
draw_arrow(3, 8.3, 3, 9.8)
draw_arrow(3, 9.8, 3.75, 9.8)

draw_box(5, 7.0, "Feature Extraction\n(MediaPipe 21 Landmarks)", color='#1f77b4')
draw_arrow(5, 6.6, 5, 6.2)

draw_box(5, 5.8, "Data Normalization &\nRelative Coordinates", color='#1f77b4')
draw_arrow(5, 5.4, 5, 5.0)

draw_box(5, 4.6, "Classification Model\n(TFLite Inference Engine)", color='#9467bd')
draw_arrow(5, 4.2, 5, 3.8)

draw_box(5, 3.4, "Arabic Text Rendering\n(Reshaper/Bidi Logic)", color='#ff7f0e')
draw_arrow(5, 3.0, 5, 2.6)

draw_box(5, 2.2, "Multimodal Feedback\n(Audio/Glassmorphism UI)", color='#2ca02c')
draw_arrow(5, 1.8, 5, 1.4)

draw_box(5, 1.0, "END / Loop Cycle", box_style='round,pad=0.1', color='red')

# Save the flowchart
output_dir = r"c:\Users\mohammed\ProjectStart\صوره"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

file_path = os.path.join(output_dir, 'system_pipeline_flowchart.png')
plt.savefig(file_path, dpi=300, bbox_inches='tight', transparent=False)
print(f"Success: Flowchart saved at {file_path}")
