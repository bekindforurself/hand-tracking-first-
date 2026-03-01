import json
import os

filepath = r'c:\Users\mohammed\ProjectStart\sign_lang_app\keypoint_classification.ipynb'

if not os.path.exists(filepath):
    print(f"Error: File {filepath} not found.")
    exit(1)

with open(filepath, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# التعديلات المطلوبة لتحسين التعلم
NEW_NUM_CLASSES = 38
FOUND_CLASSES = False
FOUND_MODEL = False

for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        source = cell['source']
        full_source = "".join(source)
        
        # 1. تحديث عدد الكلاسات
        if 'NUM_CLASSES =' in full_source:
            for i, line in enumerate(source):
                if 'NUM_CLASSES =' in line:
                    source[i] = f'NUM_CLASSES = {NEW_NUM_CLASSES}\n'
                    FOUND_CLASSES = True
        
        # 2. تحسين بناء النموذج (Model Architecture)
        if 'tf.keras.models.Sequential' in full_source:
            new_model_code = [
                "model = tf.keras.models.Sequential([\n",
                "    tf.keras.layers.Input((21 * 2, )),\n",
                "    tf.keras.layers.Dropout(0.2),\n",
                "    tf.keras.layers.Dense(64, activation='relu'),\n",
                "    tf.keras.layers.Dropout(0.4),\n",
                "    tf.keras.layers.Dense(32, activation='relu'),\n",
                "    tf.keras.layers.Dense(NUM_CLASSES, activation='softmax')\n",
                "])\n"
            ]
            cell['source'] = new_model_code
            FOUND_MODEL = True

if FOUND_CLASSES and FOUND_MODEL:
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)
    print("Successfully updated model architecture and NUM_CLASSES in the notebook.")
else:
    print(f"Status: Classes found: {FOUND_CLASSES}, Model found: {FOUND_MODEL}")
