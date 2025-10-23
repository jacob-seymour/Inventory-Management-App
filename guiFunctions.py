import ttkbootstrap as ttk
from tkinter import filedialog, messagebox, END
from backend import *
import threading

# --- Event Handlers ---
def on_pallet_select(event, widgets):
    """
    Event handler for when a pallet is selected in the 'Add Items' tab.
    Fetches the corresponding model number and updates the UI.
    """
    combo_model = widgets['combo_model']
    combo_pallet = widgets['combo_pallet']
    
    pallet_id = combo_pallet.get()
    
    # Re-enable model combo for changes
    combo_model.config(state="normal")
    
    if not pallet_id:
        # If pallet is cleared, clear model and make it selectable again
        combo_model.set('')
        combo_model.config(state="readonly")
        return

    # Fetch model number from backend
    model_number = get_model_for_pallet(pallet_id)
    
    if model_number:
        combo_model.set(model_number)
        combo_model.config(state="disabled") # Lock the model number
    else:
        # If pallet not found, clear model and allow manual selection
        combo_model.set('')
        combo_model.config(state="readonly")
        messagebox.showwarning("Not Found", f"No model number found for Pallet ID: {pallet_id}")

# --- Core GUI Actions ---

def gui_bulk_add_serials(widgets):
    """Add multiple items with serial numbers based on the selected pallet."""
    text_serials = widgets['text_serials']
    combo_pallet = widgets['combo_pallet']

    serials = text_serials.get("1.0", "end").strip().splitlines()
    pallet_id = combo_pallet.get()

    if not serials or not pallet_id:
        messagebox.showwarning("Missing Data", "Please provide Serial Numbers and select a Pallet ID.")
        return

    # More efficient: Get product_id directly from pallet table
    resp = supabase.table("pallet").select("product_id").eq("pallet_id", pallet_id).execute()
    if not resp.data:
        messagebox.showerror("Error", f"Could not find Pallet ID: {pallet_id} in the database.")
        return
    product_id = resp.data[0]["product_id"]

    # Get next item_id
    resp_max = supabase.table("item").select("item_id").order("item_id", desc=True).limit(1).execute()
    next_id = (resp_max.data[0]["item_id"] + 1) if resp_max.data else 1

    # Prepare items for insertion
    items_to_insert = []
    for serial in serials:
        serial = serial.strip()
        if serial:
            items_to_insert.append({
                "item_id": next_id,
                "serial_number": serial,
                "pallet_id": str(pallet_id).strip(),
                "product_id": product_id,
            })
            next_id += 1

    count = bulkScanItems(items_to_insert, ignore_conflicts=False)
    messagebox.showinfo("Success", f"Inserted {count} items.")
    
    # Clear form
    text_serials.delete("1.0", "end")
    combo_pallet.set('')
    # Trigger the event handler to reset the model combobox
    on_pallet_select(None, widgets)

# Thread-safe data fetching
def fetch_data_for_dropdowns(app, widgets):
    """
    Fetches model numbers and pallet IDs from backend in background thread.
    Uses cached data when available for faster loading.
    """
    try:
        model_numbers = fetch_model_numbers()
        pallet_ids = fetch_pallet_ids()
        
        # Schedule GUI update on main thread
        app.after(0, lambda: update_dropdowns_in_gui(widgets, model_numbers, pallet_ids))
    except Exception as e:
        print(f"Failed to fetch initial data: {e}")
        app.after(0, lambda: messagebox.showerror("Network Error", 
            "Could not fetch initial data from the database. Please check your connection."))

def update_dropdowns_in_gui(widgets, model_numbers, pallet_ids):
    """Update comboboxes with fetched data (runs on main thread)."""
    # Convert tuples to lists for combobox
    model_list = list(model_numbers) if model_numbers else []
    pallet_list = list(pallet_ids) if pallet_ids else []
    
    widgets['combo_model']['values'] = model_list
    widgets['combo_pallet']['values'] = pallet_list
    widgets['combo_view_pallet']['values'] = pallet_list
    widgets['combo_view_model']['values'] = model_list
    widgets['combo_product_model']['values'] = model_list
    widgets['combo_remove_pallet']['values'] = pallet_list
    widgets['combo_modify_pallet_select']['values'] = pallet_list # Added new combobox
    
    # Clear "Loading..." text
    if widgets['combo_model'].get() == "Loading...":
        widgets['combo_model'].set('')
    if widgets['combo_pallet'].get() == "Loading...":
        widgets['combo_pallet'].set('')
    if widgets['combo_view_pallet'].get() == "Loading...":
        widgets['combo_view_pallet'].set('')
    if widgets['combo_view_model'].get() == "Loading...":
        widgets['combo_view_model'].set('')
    if widgets['combo_product_model'].get() == "Loading...":
        widgets['combo_product_model'].set('')
    if widgets['combo_remove_pallet'].get() == "Loading...":
        widgets['combo_remove_pallet'].set('')
    if widgets['combo_modify_pallet_select'].get() == "Loading...": # Added new combobox
        widgets['combo_modify_pallet_select'].set('')
    
    print("Dropdowns updated with fresh data.")

def gui_bulk_remove(widgets):
    """Remove multiple items by serial number."""
    text_bulk_remove = widgets['text_bulk_remove']
    sns = text_bulk_remove.get("1.0", "end").strip().splitlines()
    
    if not sns:
        messagebox.showwarning("Warning", "No serial numbers entered")
        return
    
    count = bulkRemoveItems(sns)
    messagebox.showinfo("Success", f"Removed {count} items.")
    text_bulk_remove.delete("1.0", "end")

def gui_import_csv():
    """Import items from CSV file."""
    path = filedialog.askopenfilename(title="Select CSV File", filetypes=[("CSV", "*.csv")])
    if not path:
        return
    
    count = importFromCsv(path)
    messagebox.showinfo("Import Complete", f"Imported {count} items from {path}")

def gui_view_by_pallet(widgets):
    """Display items filtered by pallet ID."""
    combo_view_pallet = widgets['combo_view_pallet']
    tree_items = widgets['tree_items']
    
    pid = combo_view_pallet.get()
    if not pid:
        messagebox.showwarning("Missing Data", "Select a pallet ID")
        return
    
    rows = selectItemsByPallet(pid)
    
    # Clear and populate tree
    tree_items.delete(*tree_items.get_children())
    for row in rows:
        tree_items.insert('', 'end', values=row)

def gui_view_by_product(widgets):
    """Display items filtered by model number."""
    combo_view_model = widgets['combo_view_model']
    tree_items_product = widgets['tree_items_product']

    model_number = combo_view_model.get()
    if not model_number:
        messagebox.showwarning("Missing Data", "Select a model number")
        return
    
    # Get product_id for model
    resp = supabase.table("product").select("product_id").eq("model_number", model_number).execute()
    if not resp.data:
        messagebox.showerror("Error", f"No product found for model {model_number}")
        return
    
    product_id = resp.data[0]["product_id"]
    rows = selectItemsByProduct(product_id)
    
    # Clear and populate tree
    tree_items_product.delete(*tree_items_product.get_children())
    for row in rows:
        tree_items_product.insert('', 'end', values=row)

def gui_view_by_aisle(widgets):
    """Display pallets filtered by aisle."""
    combo_view_aisle = widgets['combo_view_aisle']
    tree_aisle_pallets = widgets['tree_aisle_pallets']

    aisle = combo_view_aisle.get()
    if not aisle or aisle == "Select an Aisle":
        messagebox.showwarning("Missing Data", "Please select an aisle from the dropdown.")
        return
    
    rows = viewPalletByAisle(aisle)

    tree_aisle_pallets.delete(*tree_aisle_pallets.get_children())
    for row in rows:
        # The backend function returns a dict, so get values in order for the tree
        tree_aisle_pallets.insert('', 'end', values=(row["pallet_id"], row["shelf_id"], row["model_number"]))

def gui_add_product(widgets):
    """Add a new product to database."""
    entry_prod_name = widgets['entry_prod_name']
    entry_prod_desc = widgets['entry_prod_desc']
    entry_model_num = widgets['entry_model_num']

    # Get next product_id
    resp_max = supabase.table("product").select("product_id").order("product_id", desc=True).limit(1).execute()
    
    try:
        pid = resp_max.data[0]["product_id"] + 1 if resp_max.data else 1
        pname = entry_prod_name.get().strip()
        pdesc = entry_prod_desc.get().strip()
        mnum = entry_model_num.get().strip()

        if not pname or not mnum:
            messagebox.showwarning("Missing Data", "Product Name and Model Number are required.")
            return

        success = addProduct(pid, pname, pdesc, mnum)
        if success:
            messagebox.showinfo("Success", f"Product {pname} added successfully.")
            
            # Clear form
            entry_prod_name.delete(0, END)
            entry_prod_desc.delete(0, END)
            entry_model_num.delete(0, END)
            
            # Clear cache and refresh dropdowns
            clear_dropdown_cache()
            refresh_all_dropdowns(widgets['app'], widgets)
        else:
            messagebox.showerror("Error", "Could not add product.")
    except ValueError:
        messagebox.showerror("Error", "Product ID must be an integer.")

def gui_add_pallet(widgets):
    """Add a new pallet to database."""
    entry_pallet_id = widgets['entry_pallet_id']
    entry_shelf_id = widgets['entry_shelf_id']
    combo_product_model = widgets['combo_product_model']
    entry_notes = widgets['entry_notes']
    
    pid = entry_pallet_id.get().strip()
    sid = entry_shelf_id.get().strip()
    model_number = combo_product_model.get().strip()
    notes = entry_notes.get().strip() or "N/A"

    if not pid or not sid or not model_number:
        messagebox.showwarning("Missing Data", "Pallet ID, Shelf ID, and Product are required.")
        return

    # Get product_id for model
    resp = supabase.table("product").select("product_id").eq("model_number", model_number).execute()
    if not resp.data:
        messagebox.showerror("Error", f"No product found for model {model_number}")
        return
    product_id = resp.data[0]["product_id"]

    success = addPallet(pid, sid, product_id, notes)
    if success:
        messagebox.showinfo("Success", f"Pallet {pid} added successfully.")
        
        # Clear form
        entry_pallet_id.delete(0, END)
        entry_shelf_id.delete(0, END)
        combo_product_model.set('')
        entry_notes.delete(0, END)
        
        # Clear cache and refresh dropdowns
        clear_dropdown_cache()
        refresh_all_dropdowns(widgets['app'], widgets)
    else:
        messagebox.showerror("Error", "Could not add pallet.")

def gui_remove_pallet(widgets):
    """GUI action to remove a pallet and all its associated items."""
    combo_remove_pallet = widgets['combo_remove_pallet']
    pallet_id = combo_remove_pallet.get()
    
    if not pallet_id:
        messagebox.showwarning("Missing Data", "Please select a Pallet ID to remove.")
        return

    # Ask for confirmation
    confirm = messagebox.askyesno(
        "Confirm Deletion",
        f"Are you sure you want to delete Pallet '{pallet_id}'?\n\n"
        f"WARNING: This will also delete ALL items currently on this pallet.\n"
        f"This action cannot be undone."
    )
    
    if not confirm:
        return # User clicked No

    try:
        success = removePallet(pallet_id) # Call the backend function
        
        if success:
            messagebox.showinfo("Success", f"Pallet {pallet_id} and all its items were successfully removed.")
            
            # Clear the selection
            combo_remove_pallet.set('')
            
            # Clear cache and refresh all dropdowns
            clear_dropdown_cache()
            refresh_all_dropdowns(widgets['app'], widgets)
        else:
            messagebox.showerror("Error", f"Could not remove pallet {pallet_id}. It may have already been deleted or another error occurred. Check the console.")
            
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {e}")

def gui_update_pallet_shelf(widgets):
    """GUI action to update the shelf ID of an existing pallet."""
    combo_select = widgets['combo_modify_pallet_select']
    entry_shelf = widgets['entry_new_shelf_id']
    
    pallet_id = combo_select.get()
    new_shelf_id = entry_shelf.get().strip()
    
    if not pallet_id or not new_shelf_id:
        messagebox.showwarning("Missing Data", "Please select a pallet AND enter a new shelf ID.")
        return

    try:
        success = updatePalletShelf(pallet_id, new_shelf_id)
        
        if success:
            messagebox.showinfo("Success", f"Pallet {pallet_id} location updated to {new_shelf_id}.")
            
            # Clear form
            combo_select.set('')
            entry_shelf.delete(0, END)
            
            # Note: No dropdown refresh is needed, but the change
            # will be visible if the user visits the 'Pallet Info'
            # or 'View by Aisle' tabs, as they reload data.
        else:
            messagebox.showerror("Error", f"Could not update pallet {pallet_id}. It may not exist.")
            
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {e}")

def load_stock_counts(tree_stock):
    """Load stock counts by model into treeview."""
    tree_stock.delete(*tree_stock.get_children())
    data = countItemsByModel()
    for row in data:
        tree_stock.insert("", END, values=(row["model_number"], row["count"]))

def load_pallet_counts(tree_pallet_counts):
    """Load pallet counts by model into treeview."""
    tree_pallet_counts.delete(*tree_pallet_counts.get_children())
    data = countPalletsByModel()
    for row in data:
        tree_pallet_counts.insert("", END, values=(row["model_number"], row["pallet_count"]))

def load_pallet_info(tree_pallet_info):
    """Load pallet info into treeview."""
    tree_pallet_info.delete(*tree_pallet_info.get_children())
    data = getPalletInfo()
    for row in data:
        tree_pallet_info.insert("", END, values=(row["pallet_id"], row["shelf_id"], row["model_number"]))

def refresh_all_dropdowns(app, widgets):
    """Refresh dropdown data in background thread."""
    print("Refreshing dropdown data in background...")
    threading.Thread(target=fetch_data_for_dropdowns, args=(app, widgets), daemon=True).start()

def on_tab_change(event, widgets):
    """Handle tab change events - load data as needed."""
    app = widgets['app']
    try:
        tab_text = event.widget.tab(event.widget.select(), "text")
    except Exception:
        return # Error getting tab, probably during startup

    # Only refresh dropdowns for tabs that need them
    if tab_text in ("Manage Items", "View by Pallet", "View by Model", "Manage Pallets"): # Updated tab name
        refresh_all_dropdowns(app, widgets)
    elif tab_text == "Stock Counts":
        load_stock_counts(widgets['tree_stock'])
    elif tab_text == "Pallet Counts":
        load_pallet_counts(widgets['tree_pallet_counts'])
    elif tab_text == 'Pallet Info':
        load_pallet_info(widgets['tree_pallet_info'])
