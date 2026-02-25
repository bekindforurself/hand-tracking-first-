import json

filepath = r'c:\Users\mohammed\ProjectStart\sign_lang_app\keypoint_classification.ipynb'

with open(filepath, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Total lines in labels file is 38
NEW_NUM_CLASSES = 38

found = False
for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        source = cell['source']
        for i, line in enumerate(source):
            if 'NUM_CLASSES =' in line:
                source[i] = f'    "NUM_CLASSES = {NEW_NUM_CLASSES}"\n' if line.strip().startswith('"') else f'NUM_CLASSES = {NEW_NUM_CLASSES}\n'
                found = True
                break
        if found:
            break

if found:
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)
    print(f"Successfully updated NUM_CLASSES to {NEW_NUM_CLASSES}.")
else:
    print("Could not find NUM_CLASSES definition in any code cell.")
