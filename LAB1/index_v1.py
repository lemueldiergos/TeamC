import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
import webbrowser

class RoboticsModelingTool3D:
    def __init__(self, root):
        self.root = root
        self.root.title("Robotics Modeling Tool (3D)")
        # Load and resize the image
        image = Image.open("robotics.png")
        image = image.resize((650, 400))
        self.robot_image = ImageTk.PhotoImage(image)
        # Display the image
        self.image_label = tk.Label(root, image=self.robot_image)
        self.image_label.grid(row=0, column=0, columnspan=4)
        # Prompt for the number of joints and maximum link length
        self.num_joints_label = tk.Label(root, text="Number of Joints:")
        self.num_joints_label.grid(row=1, column=0)
        self.num_joints_entry = tk.Entry(root)
        self.num_joints_entry.grid(row=1, column=1)
        self.max_length_label = tk.Label(root, text="Max. Link Length:")
        self.max_length_label.grid(row=2, column=0)
        self.max_length_entry = tk.Entry(root)
        self.max_length_entry.grid(row=2, column=1)
        self.num_joints_entry.bind("<Return>", lambda event:self.create_joints())
        self.max_length_entry.bind("<Return>", lambda event:self.create_joints())
        self.num_joints_button = tk.Button(root, text="Submit", command=self.create_joints)
        self.num_joints_button.grid(row=3, column=0, columnspan=2, sticky="e")
# Initialize joint coordinates and link lengths lists
        self.joint_coordinates = []
        self.link_lengths = []
# Create a matplotlib 3D figure
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.plot = self.figure.add_subplot(111, projection='3d')
        self.canvas = FigureCanvasTkAgg(self.figure, master=root)
        self.canvas.get_tk_widget().grid(row=10, column=0, columnspan=4)
        self.canvas.get_tk_widget().grid_remove()
        
    def create_joints(self):
            try:
                num_joints = int(self.num_joints_entry.get())
                max_length = float(self.max_length_entry.get())
                if num_joints < 2:
                    raise ValueError("Number of joints must be at least 2")
                if max_length <= 0:
                    raise ValueError("Max. length must be greater than 0")
                # Clear existing widgets
                for widget in self.root.winfo_children():
                    if widget != self.canvas.get_tk_widget():
                        widget.destroy()
                # Automatically set Joint 1 to (0, 0, 0)
                self.joint_coordinates = [(0, 0, 0)]
                # Create entry fields for joints and links
                for i in range(1, num_joints):
                # Joint coordinates
                    joint_label = tk.Label(self.root, text=f"Joint {i+1}:")
                    joint_label.grid(row=i+2, column=0)
                    joint_entry_x = tk.Entry(self.root)
                    joint_entry_x.grid(row=i+2, column=1)
                    joint_entry_y = tk.Entry(self.root)
                    joint_entry_y.grid(row=i+2, column=2)
                    joint_entry_z = tk.Entry(self.root)
                    joint_entry_z.grid(row=i+2, column=3)
                    joint_entry_x.bind("<Return>", lambda event, idx=i-1:
                        self.compute_link_length(idx, max_length))
                    joint_entry_y.bind("<Return>", lambda event, idx=i-1:
                        self.compute_link_length(idx, max_length))
                    joint_entry_z.bind("<Return>", lambda event, idx=i-1:
                        self.compute_link_length(idx, max_length))
                    self.joint_coordinates.append((0, 0, 0)) # Initialize to
                        # Link lengths
                    link_label = tk.Label(self.root, text=f"Link {i}:")
                    link_label.grid(row=i+2, column=4)
                    link_entry = tk.Entry(self.root, state='readonly')
                    link_entry.grid(row=i+2, column=5)
                    self.link_lengths.append(link_entry)
# Show and update the plot
                    self.canvas.get_tk_widget().grid(row=10, column=0, columnspan=4)
                    self.update_plot()
                    # Create button for opening pythonrobotics.io
                    self.open_pythonrobotics_button = tk.Button(root, text="Learn More", command=self.open_pythonrobotics)

                    self.open_pythonrobotics_button.grid(row=11, column=0, columnspan=4, pady=(10, 0), sticky="e")

            except ValueError as e:
                messagebox.showerror("Error", str(e))
                self.num_joints_entry.delete(0, tk.END)
                self.max_length_entry.delete(0, tk.END)
            
    def compute_link_length(self, idx, max_length):
        try:
            x1, y1, z1 = self.joint_coordinates[idx]
            x2 = float(self.root.grid_slaves(idx+3, 1)[0].get())
            y2 = float(self.root.grid_slaves(idx+3, 2)[0].get())
            z2 = float(self.root.grid_slaves(idx+3, 3)[0].get())
            link_length = ((x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2) ** 0.5
            if link_length > max_length:
                link_length = None # Set to None if exceeds maximum length
                if idx < len(self.link_lengths):
                    if link_length is not None:
                        self.link_lengths[idx].config(state='normal')
                        self.link_lengths[idx].delete(0, tk.END)
                        self.link_lengths[idx].insert(0, f"{link_length:.2f}")
                        self.link_lengths[idx].config(state='readonly')
                    else:
                        self.link_lengths[idx].config(state='normal')
                        self.link_lengths[idx].delete(0, tk.END)
                        self.link_lengths[idx].insert(0, "Exceeds Max Length")
                        self.link_lengths[idx].config(state='readonly')
                        self.joint_coordinates[idx] = (x2, y2, z2)
                        self.update_plot()
        except ValueError:
            pass


    def update_plot(self):
        self.plot.clear()
        x_values = [coord[0] for coord in self.joint_coordinates]
        y_values = [coord[1] for coord in self.joint_coordinates]
        z_values = [coord[2] for coord in self.joint_coordinates]
        self.plot.plot(x_values, y_values, z_values, marker='o', color='b')
        self.plot.scatter(x_values[0], y_values[0], z_values[0], marker='o', color='r', label='Base Joint')
        green_box_x = [x_values[-1], x_values[-1], x_values[-1], x_values[-1], x_values[-1]]
        green_box_y = [y_values[-1], y_values[-1], y_values[-1], y_values[-1], y_values[-1]]
        green_box_z = [z_values[-1], z_values[-1], z_values[-1], z_values[-1], z_values[-1] + 0.5] # Extend in the z-direction
        self.plot.plot(green_box_x, green_box_y, green_box_z, color='g',label='End-Effector')
        self.plot.set_xlabel('X')
        self.plot.set_ylabel('Y')
        self.plot.set_zlabel('Z')
        self.plot.set_title('Robotics Model (3D)')
        self.plot.legend()
        self.canvas.draw()

    def open_pythonrobotics(self):
        webbrowser.open_new("https://pythonrobotics.io/")

if __name__ == "__main__":
    root = tk.Tk()
    app = RoboticsModelingTool3D(root)
    root.mainloop()