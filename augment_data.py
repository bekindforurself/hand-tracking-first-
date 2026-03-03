import csv
import numpy as np
import random
import os
from collections import Counter

def augment_points(points, rotate_range=15, scale_range=0.1, noise_level=0.01):
    """توليد نقاط مشوهة عشوائياً لمحاكاة اختلاف حركات الناس"""
    pts = np.array(points).reshape(-1, 2)
    
    # 1. دوران عشوائي (لمحاكاة ميلان اليد)
    angle = np.radians(random.uniform(-rotate_range, rotate_range))
    rotation_matrix = np.array([
        [np.cos(angle), -np.sin(angle)],
        [np.sin(angle),  np.cos(angle)]
    ])
    pts = np.dot(pts, rotation_matrix)
    
    # 2. تغيير الحجم عشوائياً (لمحاكاة بعد وقرب اليد)
    scale = random.uniform(1 - scale_range, 1 + scale_range)
    pts *= scale
    
    # 3. نويز عشوائي (لمحاكاة اهتزاز اليد)
    pts += np.random.normal(0, noise_level, pts.shape)
    
    return pts.flatten().tolist()

input_file = 'model/keypoint_classifier/keypoint.csv'
backup_file = 'model/keypoint_classifier/keypoint.original.csv'

if not os.path.exists(backup_file):
    import shutil
    shutil.copy(input_file, backup_file)
    print(f"Backup created: {backup_file}")

# قراءة كل البيانات الموجودة
all_data = []
labels_count = Counter()

with open(input_file, 'r', newline='') as f:
    reader = csv.reader(f)
    for row in reader:
        if not row: continue
        label = int(row[0])
        points = [float(x) for x in row[1:]]
        all_data.append((label, points))
        labels_count[label] += 1

print(f"Current labels distribution: {dict(sorted(labels_count.items()))}")

# توليد بيانات إضافية لكل حرف
augmented_rows = []
TARGET_AUGMENT_PER_LABEL = 500 # سنضيف 500 عينة لكل حرف لزيادة الذكاء

print(f"Generating {TARGET_AUGMENT_PER_LABEL} samples for EACH of the {len(labels_count)} labels...")

for label in labels_count:
    # الحصول على العينات الأصلية لهذا الحرف فقط
    original_samples = [pts for lbl, pts in all_data if lbl == label]
    
    for _ in range(TARGET_AUGMENT_PER_LABEL):
        orig = random.choice(original_samples)
        new_pts = augment_points(orig)
        augmented_rows.append([label] + new_pts)

# إضافة البيانات الجديدة للملف
with open(input_file, 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(augmented_rows)

print(f"Success! Total new samples added: {len(augmented_rows)}")
print("Your dataset is now much more 'diverse' and understands different hand variations.")
print("Proceed to retrain the model in your Jupyter notebook.")
