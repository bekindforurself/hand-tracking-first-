import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split
import os

# المسارات
dataset = 'model/keypoint_classifier/keypoint_numbers.csv'
model_save_path = 'model/keypoint_classifier/keypoint_numbers_classifier.hdf5'
tflite_save_path = 'model/keypoint_classifier/keypoint_numbers_classifier.tflite'

NUM_CLASSES = 11 # من 0 إلى 10

print("--- Starting Numbers Training Process (Dual Hand) ---")

# 1. تحميل البيانات
X_dataset = np.loadtxt(dataset, delimiter=',', dtype='float32', usecols=list(range(1, 85)))
y_dataset = np.loadtxt(dataset, delimiter=',', dtype='int32', usecols=(0))

X_train, X_test, y_train, y_test = train_test_split(X_dataset, y_dataset, train_size=0.75, random_state=42)

# 2. بناء النموذج (أكبر قليلاً للتعامل مع نقاط اليدين)
model = tf.keras.models.Sequential([
    tf.keras.layers.Input((84, )),
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dropout(0.4),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dense(32, activation='relu'),
    tf.keras.layers.Dense(NUM_CLASSES, activation='softmax')
])

model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

# 3. التدريب
print("Training the numbers model... please wait.")
model.fit(
    X_train,
    y_train,
    epochs=1000,
    batch_size=128,
    validation_data=(X_test, y_test),
    callbacks=[tf.keras.callbacks.EarlyStopping(patience=30, restore_best_weights=True)],
    verbose=1
)

# 4. الحفظ والتحويل
model.save(model_save_path, include_optimizer=False)
converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
tflite_model = converter.convert()

with open(tflite_save_path, 'wb') as f:
    f.write(tflite_model)

print(f"--- SUCCESS! Numbers Model saved to {tflite_save_path} ---")
