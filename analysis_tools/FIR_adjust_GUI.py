import tkinter as tk

# Define the window
root = tk.Tk()
root.geometry("1000x500")
masterFrame = tk.Frame(root)
masterFrame.pack()

# define a frame on the left side
signalView = tk.Frame(root)
signalView.pack(side="left")

# define a frame on the right side
controlBox = tk.Frame(root)
controlBox.pack(side="right")
controlBox_Header = tk.Label(controlBox, text="Control Box")
controlBox_Header.pack()

# Filter Type Control Options box
applyButton = tk.Button(masterFrame, text="Apply Changes")
applyButton.pack(padx=5, pady=6)

controlBox_filterOptionsSelector = tk.LabelFrame(masterFrame,
                                                text="Filter Options",
                                                labelanchor="n",
                                                labelwidget=applyButton,
                                                relief="raised")





root.title("FIR Filter Adjuster")

# Launch
root.mainloop()