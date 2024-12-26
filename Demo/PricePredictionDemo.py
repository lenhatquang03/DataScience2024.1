import pickle as pkl
import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import os

rf_model = pkl.load(open(os.path.join("Models/RandomForest.h5"), 'rb'))

df_display = pd.read_csv("clean_data.csv").drop("Unnamed: 0", axis = 1)

df = pd.read_csv("Demo/RandomForest/test_features.csv")
df.rename(columns= {"Unnamed: 0": "Index"}, inplace= True)
df.set_index("Index", inplace = True)

y = pd.read_csv("Demo/RandomForest/test_targets.csv")
y.rename(columns= {"Unnamed: 0": "Index"}, inplace= True)
y.set_index("Index", inplace = True)


def update_record_and_predict():
    try:
        idx = np.random.choice(df.index)
        record = df.loc[idx]
        display_record = df_display.iloc[idx]

        for i, col in enumerate(df_display.columns):
            treeview.item(i+1, values=(col, display_record[col]))

        prediction = rf_model.predict(pd.DataFrame([record]))
        prediction_label.config(
            text=f"Actual Price: {y.loc[idx].values[0]:.3f} billion VND\nPredicted Price: {prediction[0]:.3f} billion VND"
        )
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

def create_gui():
    window = tk.Tk()
    window.title("Real Estate Price Prediction")
    window.geometry("800x600")
    window.config(bg="#f5f5f5")

    title_label = tk.Label(window, text="Randomly Selected Record", font=("Arial", 20, "bold"), bg="#f5f5f5")
    title_label.pack(pady=20)

    frame = tk.Frame(window, bg="#f5f5f5")
    frame.pack(padx=20, pady=10, fill=tk.X)
    
    global treeview
    treeview = ttk.Treeview(frame, columns=("Attribute", "Value"), show="headings", height=14)
    treeview.pack(pady=10, fill=tk.X)
    treeview.heading("Attribute", text="Attribute", anchor="w")
    treeview.heading("Value", text="Value", anchor="w")
    for i in range(len(df_display.columns)):
        treeview.insert("", "end", iid=i+1, values=("", ""))

    global prediction_label
    prediction_label = tk.Label(window, text="Predicted Value: ", font=("Arial", 16, "bold"), bg="#f5f5f5", fg="#333")
    prediction_label.pack(pady=20)

    new_record_button = tk.Button(window, text="Try New Record", command=update_record_and_predict, font=("Arial", 14), bg="#4CAF50", fg="black", relief="raised", padx=10, pady=5)
    new_record_button.pack(pady=15)

    update_record_and_predict()
    window.mainloop()

create_gui()
