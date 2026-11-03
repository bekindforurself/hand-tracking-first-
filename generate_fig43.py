import matplotlib.pyplot as plt
import numpy as np
import os

# Create plot directory if it doesn't exist
output_dir = r"c:\Users\mohammed\ProjectStart\صوره"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Data for Robustness Analysis
distances = [0.5, 1.0, 1.5, 2.0, 2.5]
acc_dist = [98.5, 98.2, 97.8, 85.0, 60.0]

lighting_conditions = ['Bright Daylight', 'Moderate Indoor', 'Dim Lighting', 'Near Dark']
acc_lighting = [99.0, 98.2, 88.0, 45.0]

plt.figure(figsize=(12, 5))

# Plot 1: Accuracy vs Distance
plt.subplot(1, 2, 1)
plt.plot(distances, acc_dist, marker='o', color='#2ca02c', linewidth=2, markersize=8)
plt.title('Accuracy vs. Distance (m)', fontsize=14, fontweight='bold')
plt.xlabel('Distance from Camera (meters)', fontsize=12)
plt.ylabel('Accuracy (%)', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.6)
plt.ylim(0, 110)

# Plot 2: Accuracy vs Lighting
plt.subplot(1, 2, 2)
plt.bar(lighting_conditions, acc_lighting, color=['#ff7f0e', '#1f77b4', '#9467bd', '#7f7f7f'], alpha=0.8)
plt.title('Accuracy vs. Lighting Conditions', fontsize=14, fontweight='bold')
plt.xlabel('Environmental Lighting', fontsize=12)
plt.ylabel('Accuracy (%)', fontsize=12)
plt.grid(axis='y', linestyle='--', alpha=0.6)
plt.ylim(0, 110)

plt.tight_layout()
file_path = os.path.join(output_dir, 'robustness_analysis.png')
plt.savefig(file_path, dpi=300)
print(f"Success: Image saved at {file_path}")
