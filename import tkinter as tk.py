import tkinter as tk
from tkinter import ttk, messagebox

class Block:
    def __init__(self, size):
        self.size = size
        self.free = True
        self.id = 0

class MemorySimulatorGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Memory Allocation Simulator")
        self.geometry("1000x550")
        self.configure(bg="#f2f2f2")
        self.memory = []
        self.next_alloc_id = 1

        self.init_default_memory()
        self.create_widgets()
        self.draw_canvas()

    # ---------------- Initialize default memory ---------------- #
    def init_default_memory(self):
        # Example initial blocks
        initial_sizes = [100, 500, 200, 300, 600]
        self.memory = [Block(size) for size in initial_sizes]

    # ---------------- GUI Layout ---------------- #
    def create_widgets(self):
        # Left frame: controls
        left_frame = ttk.Frame(self, padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.Y)

        ttk.Label(left_frame, text="Memory Allocation Simulator", font=("Arial", 14, "bold")).pack(anchor="center", pady=5)

        # Allocation
        alloc_frame = ttk.LabelFrame(left_frame, text="Allocate Process", padding=10)
        alloc_frame.pack(fill=tk.X, pady=10)
        ttk.Label(alloc_frame, text="Process Size:").grid(row=0, column=0, sticky="w")
        self.req_entry = ttk.Entry(alloc_frame, width=15)
        self.req_entry.grid(row=0, column=1, pady=2, padx=5)
        ttk.Label(alloc_frame, text="Strategy:").grid(row=1, column=0, sticky="w")
        self.strategy = tk.StringVar(value="first")
        ttk.Radiobutton(alloc_frame, text="First Fit", variable=self.strategy, value="first").grid(row=1, column=1, sticky="w")
        ttk.Radiobutton(alloc_frame, text="Best Fit", variable=self.strategy, value="best").grid(row=2, column=1, sticky="w")
        ttk.Radiobutton(alloc_frame, text="Worst Fit", variable=self.strategy, value="worst").grid(row=3, column=1, sticky="w")
        ttk.Button(alloc_frame, text="Allocate", command=self.allocate_process).grid(row=4, column=0, columnspan=2, pady=5, sticky="we")

        # Deallocation
        dealloc_frame = ttk.LabelFrame(left_frame, text="Deallocate Process", padding=10)
        dealloc_frame.pack(fill=tk.X, pady=10)
        ttk.Label(dealloc_frame, text="Allocation ID:").grid(row=0, column=0, sticky="w")
        self.dealloc_entry = ttk.Entry(dealloc_frame, width=15)
        self.dealloc_entry.grid(row=0, column=1, pady=2, padx=5)
        ttk.Button(dealloc_frame, text="Deallocate", command=self.deallocate_process).grid(row=1, column=0, columnspan=2, pady=5, sticky="we")

        # Actions
        action_frame = ttk.Frame(left_frame)
        action_frame.pack(fill=tk.X, pady=10)
        ttk.Button(action_frame, text="Show Memory Table", command=self.show_table).pack(fill=tk.X, pady=2)
        ttk.Button(action_frame, text="Reset Simulator", command=self.reset).pack(fill=tk.X, pady=2)

        # Right frame: canvas
        right_frame = ttk.Frame(self, padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.canvas = tk.Canvas(right_frame, bg="#ffffff")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Status bar
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor="w")
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.update_status()

    # ---------------- Allocation & Deallocation ---------------- #
    def allocate_process(self):
        try:
            req = int(self.req_entry.get().strip())
            if req <= 0: raise ValueError
        except:
            messagebox.showerror("Invalid Input", "Enter positive integer for process size")
            return

        strategy = self.strategy.get()
        alloc_id = 0
        if strategy == "first":
            alloc_id = self.first_fit(req)
        elif strategy == "best":
            alloc_id = self.best_fit(req)
        elif strategy == "worst":
            alloc_id = self.worst_fit(req)

        if alloc_id:
            messagebox.showinfo("Allocated", f"Allocated with ID={alloc_id}")
        else:
            messagebox.showinfo("Failed", "Allocation failed. No suitable block.")
        self.update_status()
        self.draw_canvas()

    def deallocate_process(self):
        try:
            pid = int(self.dealloc_entry.get().strip())
        except:
            messagebox.showerror("Invalid Input", "Enter numeric allocation ID")
            return
        if self.deallocate_by_id(pid):
            messagebox.showinfo("Deallocated", f"Freed allocation ID={pid}")
        else:
            messagebox.showinfo("Not Found", f"No allocation found with ID={pid}")
        self.update_status()
        self.draw_canvas()

    def first_fit(self, req):
        for block in self.memory:
            if block.free and block.size >= req:
                block.free = False
                block.id = self.next_alloc_id
                self.next_alloc_id += 1
                return block.id
        return 0

    def best_fit(self, req):
        best = None
        best_size = float('inf')
        for block in self.memory:
            if block.free and block.size >= req and block.size < best_size:
                best = block
                best_size = block.size
        if best:
            best.free = False
            best.id = self.next_alloc_id
            self.next_alloc_id += 1
            return best.id
        return 0

    def worst_fit(self, req):
        worst = None
        worst_size = -1
        for block in self.memory:
            if block.free and block.size >= req and block.size > worst_size:
                worst = block
                worst_size = block.size
        if worst:
            worst.free = False
            worst.id = self.next_alloc_id
            self.next_alloc_id += 1
            return worst.id
        return 0

    def deallocate_by_id(self, alloc_id):
        for block in self.memory:
            if not block.free and block.id == alloc_id:
                block.free = True
                block.id = 0
                return True
        return False

    # ---------------- Draw Canvas with Equal Spacing ---------------- #
    def draw_canvas(self):
        self.canvas.delete("all")
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        num_blocks = len(self.memory)
        if num_blocks == 0: return

        # Equal width for each block
        block_width = (width - (num_blocks + 1) * 10) // num_blocks
        x = 10
        block_height = 200

        for i, block in enumerate(self.memory):
            color = "#8fd19e" if block.free else "#f08a8a"
            self.canvas.create_rectangle(x, 50, x+block_width, 50+block_height, fill=color, outline="#333")
            label = f"Idx {i+1}\nSize:{block.size}\n"
            label += "Free" if block.free else f"ID:{block.id}"
            self.canvas.create_text(x + block_width//2, 50+block_height//2, text=label, font=("Arial",10), anchor="center")
            x += block_width + 10  # spacing

    # ---------------- Memory Table ---------------- #
    def show_table(self):
        table = "Index | Size | Status\n"
        table += "---------------------\n"
        for i, block in enumerate(self.memory):
            status = "Free" if block.free else f"Allocated (ID={block.id})"
            table += f"{i+1:<5} | {block.size:<4} | {status}\n"
        top = tk.Toplevel(self)
        top.title("Memory Table")
        txt = tk.Text(top, width=50, height=15, font=("Courier",10))
        txt.pack(padx=8,pady=8)
        txt.insert("1.0", table)
        txt.config(state="disabled")
        ttk.Button(top, text="Close", command=top.destroy).pack(pady=(0,8))

    # ---------------- Reset & Status ---------------- #
    def reset(self):
        self.init_default_memory()
        self.next_alloc_id = 1
        self.update_status()
        self.draw_canvas()

    def update_status(self):
        total_free = sum(b.size for b in self.memory if b.free)
        allocated = len([b for b in self.memory if not b.free])
        self.status_var.set(f"Allocated Blocks: {allocated} | Total Free Memory: {total_free}")

if __name__=="__main__":
    app = MemorySimulatorGUI()
    app.mainloop()
