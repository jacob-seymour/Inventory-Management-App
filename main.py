import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox
from backend import *

# GUI Functions
def gui_bulk_add_serials():
    serials = text_serials.get("1.0", "end").strip().splitlines()
    model_number = combo_model.get()
    pallet_id = combo_pallet.get()

    if not serials or not model_number or not pallet_id:
        messagebox.showwarning("Missing Data", "Please fill in all fields.")
        return

    # Lookup product_id from model_number via backend
    resp = supabase.table("product").select("product_id").eq("model_number", model_number).execute()
    if not resp.data:
        messagebox.showerror("Error", f"No product found for model {model_number}")
        return
    product_id = resp.data[0]["product_id"]

    # Determine starting item_id
    resp_max = supabase.table("item").select("item_id").order("item_id", desc=True).limit(1).execute()
    next_id = (resp_max.data[0]["item_id"] + 1) if resp_max.data else 1

    items_to_insert = []
    for serial in serials:
        serial = serial.strip()
        if serial:
            items_to_insert.append((next_id, serial, pallet_id, product_id))
            next_id += 1

    count = bulkScanItems(items_to_insert, ignore_conflicts=False)
    messagebox.showinfo("Success", f"Inserted {count} items.")
    text_serials.delete("1.0", "end")
    combo_model.set('')
    combo_pallet.set('')

def gui_bulk_remove():
    sns = text_bulk_remove.get("1.0", "end").strip().splitlines()
    if not sns:
        messagebox.showwarning("Warning", "No serial numbers entered")
        return
    count = bulkRemoveItems(sns)
    messagebox.showinfo("Success", f"Removed {count} items.")

def gui_import_csv():
    path = filedialog.askopenfilename(title="Select CSV File", filetypes=[("CSV","*.csv")])
    if not path:
        return
    count = importFromCsv(path)
    messagebox.showinfo("Import Complete", f"Imported {count} items from {path}")

def gui_view_by_pallet():
    pid = combo_view_pallet.get()
    if not pid:
        messagebox.showwarning("Missing Data", "Select a pallet ID")
        return
    rows = selectItemsByPallet(pid)
    tree_items.delete(*tree_items.get_children())
    for row in rows:
        tree_items.insert('', 'end', values=row)

def gui_view_by_product():
    model_number = combo_view_model.get()
    if not model_number:
        messagebox.showwarning("Missing Data", "Select a model number")
        return
    from backend import supabase
    resp = supabase.table("product").select("product_id").eq("model_number", model_number).execute()
    if not resp.data:
        messagebox.showerror("Error", f"No product found for model {model_number}")
        return
    product_id = resp.data[0]["product_id"]
    rows = selectItemsByProduct(product_id)
    tree_items_product.delete(*tree_items_product.get_children())
    for row in rows:
        tree_items_product.insert('', 'end', values=row)

def gui_add_product():
    try:
        pid = int(entry_prod_id.get())
        pname = entry_prod_name.get().strip()
        pdesc = entry_prod_desc.get().strip()
        mnum = entry_model_num.get().strip()

        if not pname or not mnum:
            messagebox.showwarning("Missing Data", "Product Name and Model Number are required.")
            return

        success = addProduct(pid, pname, pdesc, mnum)
        if success:
            messagebox.showinfo("Success", f"Product {pname} added successfully.")
            entry_prod_id.delete(0, END)
            entry_prod_name.delete(0, END)
            entry_prod_desc.delete(0, END)
            entry_model_num.delete(0, END)
            combo_model['values'] = fetch_model_numbers()
            combo_view_model['values'] = fetch_model_numbers()
            refresh_all_dropdowns()
        else:
            messagebox.showerror("Error", "Could not add product.")
    except ValueError:
        messagebox.showerror("Error", "Product ID must be an integer.")

def gui_add_pallet():
    pid = entry_pallet_id.get().strip()
    sid = entry_shelf_id.get().strip()
    model_number = combo_product_model.get().strip()
    notes = entry_notes.get().strip() or "N/A"

    if not pid or not sid or not model_number:
        messagebox.showwarning("Missing Data", "Pallet ID, Shelf ID, and Product are required.")
        return

    # Look up product_id from model_number
    resp = supabase.table("product").select("product_id").eq("model_number", model_number).execute()
    if not resp.data:
        messagebox.showerror("Error", f"No product found for model {model_number}")
        return
    product_id = resp.data[0]["product_id"]

    success = addPallet(pid, sid, product_id, notes)
    if success:
        messagebox.showinfo("Success", f"Pallet {pid} added successfully.")
        entry_pallet_id.delete(0, END)
        entry_shelf_id.delete(0, END)
        combo_product_model.set('')
        entry_notes.delete(0, END)
        refresh_all_dropdowns()
    else:
        messagebox.showerror("Error", "Could not add pallet.")

# Main Window
app = ttk.Window(title="Inventory Manager", themename="flatly", size=(1075, 750))
tabs = ttk.Notebook(app)
tabs.pack(fill=BOTH, expand=YES, padx=10, pady=10)

# Tab 1: Add Items
tab1 = ttk.Frame(tabs)
tabs.add(tab1, text="Add Items")
frame1 = ttk.LabelFrame(tab1, text="Serial List → Items")
frame1.pack(fill=X, padx=5, pady=5)
ttk.Label(frame1, text="Serial Numbers (one per line):").grid(row=0, column=0, sticky=NW, padx=5, pady=2)
text_serials = ttk.Text(frame1, height=5)
text_serials.grid(row=0, column=1, sticky=EW, padx=5, pady=2)
ttk.Label(frame1, text="Model Number:").grid(row=1, column=0, sticky=W, padx=5, pady=2)
combo_model = ttk.Combobox(frame1, values=fetch_model_numbers(), state="readonly")
combo_model.grid(row=1, column=1, sticky=EW, padx=5, pady=2)
ttk.Label(frame1, text="Pallet ID:").grid(row=2, column=0, sticky=W, padx=5, pady=2)
combo_pallet = ttk.Combobox(frame1, values=fetch_pallet_ids(), state="readonly")
combo_pallet.grid(row=2, column=1, sticky=EW, padx=5, pady=2)
btn_add = ttk.Button(frame1, text="Add Items", bootstyle=SUCCESS, command=gui_bulk_add_serials)
btn_add.grid(row=3, column=0, columnspan=2, pady=10)
frame1.columnconfigure(1, weight=1)

# Tab 2: Import CSV
tab2 = ttk.Frame(tabs)
tabs.add(tab2, text="Import CSV")
frame2 = ttk.LabelFrame(tab2, text="Import Items from CSV")
frame2.pack(fill=X, padx=5, pady=5)
btn_csv = ttk.Button(frame2, text="Select CSV and Import", bootstyle=INFO, command=gui_import_csv)
btn_csv.pack(pady=10)

# Tab 3: Remove Items
tab3 = ttk.Frame(tabs)
tabs.add(tab3, text="Remove Items")
frame3 = ttk.LabelFrame(tab3, text="Serial Numbers to Delete")
frame3.pack(fill=X, padx=5, pady=5)
text_bulk_remove = ttk.Text(frame3, height=5)
text_bulk_remove.pack(fill=X, padx=5, pady=5)
btn_remove = ttk.Button(frame3, text="Remove Items", bootstyle=DANGER, command=gui_bulk_remove)
btn_remove.pack(pady=5)

# Tab 4: View by Pallet
tab4 = ttk.Frame(tabs)
tabs.add(tab4, text="View by Pallet")
frame4 = ttk.LabelFrame(tab4, text="Filter Items by Pallet")
frame4.pack(fill=X, padx=5, pady=5)
ttk.Label(frame4, text="Select Pallet ID:").grid(row=0, column=0, sticky=W, padx=5, pady=2)
combo_view_pallet = ttk.Combobox(frame4, values=fetch_pallet_ids(), state="readonly")
combo_view_pallet.grid(row=0, column=1, sticky=EW, padx=5, pady=2)
btn_view = ttk.Button(frame4, text="View Items", bootstyle=PRIMARY, command=gui_view_by_pallet)
btn_view.grid(row=0, column=2, padx=5, pady=2)
frame4.columnconfigure(1, weight=1)
columns = ("item_id", "serial_number", "pallet_id", "product_id")
tree_items = ttk.Treeview(tab4, columns=columns, show="headings", bootstyle=INFO)
tree_items.pack(fill=BOTH, expand=YES, padx=5, pady=5)
for col in columns:
    tree_items.heading(col, text=col.replace("_", " ").title())

# Tab 5: View by Product
tab5 = ttk.Frame(tabs)
tabs.add(tab5, text="View by Model")

frame5 = ttk.LabelFrame(tab5, text="Filter Items by Product (Model Number)")
frame5.pack(fill=X, padx=5, pady=5)

ttk.Label(frame5, text="Select Model Number:").grid(row=0, column=0, sticky=W, padx=5, pady=2)
combo_view_model = ttk.Combobox(frame5, values=fetch_model_numbers(), state="readonly")
combo_view_model.grid(row=0, column=1, sticky=EW, padx=5, pady=2)

btn_view_product = ttk.Button(frame5, text="View Items", bootstyle=PRIMARY, command=gui_view_by_product)
btn_view_product.grid(row=0, column=2, padx=5, pady=2)

frame5.columnconfigure(1, weight=1)

columns_product = ("item_id", "serial_number", "pallet_id", "product_id")
tree_items_product = ttk.Treeview(tab5, columns=columns_product, show="headings", bootstyle=INFO)
tree_items_product.pack(fill=BOTH, expand=YES, padx=5, pady=5)

for col in columns_product:
    tree_items_product.heading(col, text=col.replace("_", " ").title())

# Tab 6: Add Product
tab6 = ttk.Frame(tabs)
tabs.add(tab6, text="Add Product")

frame6 = ttk.LabelFrame(tab6, text="Add New Product")
frame6.pack(fill=X, padx=5, pady=5)

ttk.Label(frame6, text="Product ID:").grid(row=0, column=0, sticky=W, padx=5, pady=2)
entry_prod_id = ttk.Entry(frame6)
entry_prod_id.grid(row=0, column=1, sticky=EW, padx=5, pady=2)

ttk.Label(frame6, text="Product Name:").grid(row=1, column=0, sticky=W, padx=5, pady=2)
entry_prod_name = ttk.Entry(frame6)
entry_prod_name.grid(row=1, column=1, sticky=EW, padx=5, pady=2)

ttk.Label(frame6, text="Product Description:").grid(row=2, column=0, sticky=W, padx=5, pady=2)
entry_prod_desc = ttk.Entry(frame6)
entry_prod_desc.grid(row=2, column=1, sticky=EW, padx=5, pady=2)

ttk.Label(frame6, text="Model Number:").grid(row=3, column=0, sticky=W, padx=5, pady=2)
entry_model_num = ttk.Entry(frame6)
entry_model_num.grid(row=3, column=1, sticky=EW, padx=5, pady=2)

btn_add_product = ttk.Button(frame6, text="Add Product", bootstyle=SUCCESS, command=gui_add_product)
btn_add_product.grid(row=4, column=0, columnspan=2, pady=10)

frame6.columnconfigure(1, weight=1)

# Tab 7: Add Pallet
tab7 = ttk.Frame(tabs)
tabs.add(tab7, text="Add Pallet")

frame7 = ttk.LabelFrame(tab7, text="Add New Pallet")
frame7.pack(fill=X, padx=5, pady=5)

# Pallet ID
ttk.Label(frame7, text="Pallet ID:").grid(row=0, column=0, sticky=W, padx=5, pady=2)
entry_pallet_id = ttk.Entry(frame7)
entry_pallet_id.grid(row=0, column=1, sticky=EW, padx=5, pady=2)

# Shelf ID
ttk.Label(frame7, text="Shelf ID:").grid(row=1, column=0, sticky=W, padx=5, pady=2)
entry_shelf_id = ttk.Entry(frame7)
entry_shelf_id.grid(row=1, column=1, sticky=EW, padx=5, pady=2)

# Product (dropdown by model_number)
ttk.Label(frame7, text="Product Model Number:").grid(row=2, column=0, sticky=W, padx=5, pady=2)
combo_product_model = ttk.Combobox(frame7, values=fetch_model_numbers(), state="readonly")
combo_product_model.grid(row=2, column=1, sticky=EW, padx=5, pady=2)

# Notes
ttk.Label(frame7, text="Notes:").grid(row=3, column=0, sticky=W, padx=5, pady=2)
entry_notes = ttk.Entry(frame7)
entry_notes.grid(row=3, column=1, sticky=EW, padx=5, pady=2)

btn_add_pallet = ttk.Button(frame7, text="Add Pallet", bootstyle=SUCCESS, command=gui_add_pallet)
btn_add_pallet.grid(row=4, column=0, columnspan=2, pady=10)

frame7.columnconfigure(1, weight=1)

def refresh_all_dropdowns():
    combo_model['values'] = fetch_model_numbers()
    combo_pallet['values'] = fetch_pallet_ids()
    combo_view_pallet['values'] = fetch_pallet_ids()
    combo_view_model['values'] = fetch_model_numbers()
    combo_product_model['values'] = fetch_model_numbers()

def on_tab_change(event):
    tab_text = event.widget.tab(event.widget.select(), "text")
    if tab_text in ("Add Items", "View by Pallet", "View by Product", "Add Pallet"):
        refresh_all_dropdowns()

tabs.bind("<<NotebookTabChanged>>", on_tab_change)

# Run the app
app.mainloop()