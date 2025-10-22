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
    
    # Check if each key exists before trying to access it
    if 'combo_model' in widgets:
        widgets['combo_model']['values'] = model_list
        if widgets['combo_model'].get() == "Loading...":
            widgets['combo_model'].set('')

    if 'combo_pallet' in widgets:
        widgets['combo_pallet']['values'] = pallet_list
        if widgets['combo_pallet'].get() == "Loading...":
            widgets['combo_pallet'].set('')
            
    if 'combo_view_pallet' in widgets:
        widgets['combo_view_pallet']['values'] = pallet_list
        if widgets['combo_view_pallet'].get() == "Loading...":
            widgets['combo_view_pallet'].set('')

    if 'combo_view_model' in widgets:
        widgets['combo_view_model']['values'] = model_list
        if widgets['combo_view_model'].get() == "Loading...":
            widgets['combo_view_model'].set('')
            
    if 'combo_product_model' in widgets:
        widgets['combo_product_model']['values'] = model_list
        if widgets['combo_product_model'].get() == "Loading...":
            widgets['combo_product_model'].set('')

    print("Dropdowns updated with fresh data.")

def gui_view_by_pallet(widgets):
    """Display items filtered by pallet ID and show shelf location."""
    # --- Get widgets from the dictionary ---
    combo_view_pallet = widgets['combo_view_pallet']
    tree_items = widgets['tree_items']
    shelf_id_label = widgets['shelf_id_label']  # Get the shelf label widget

    pid = combo_view_pallet.get()
    if not pid:
        messagebox.showwarning("Missing Data", "Select a pallet ID")
        return

    # --- Fetch and display the shelf location ---
    shelf_id = get_shelf_for_pallet(pid)  # Call backend to get shelf ID
    if shelf_id:
        shelf_id_label.config(text=f"Shelf Location: {shelf_id}")
    else:
        shelf_id_label.config(text="Shelf Location: Not Found")

    # --- Fetch and display items for the selected pallet ---
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
    
    # Clear and populate tree
    tree_aisle_pallets.delete(*tree_aisle_pallets.get_children())
    for row in rows:
        # The backend function returns a dict, so get values in order for the tree
        tree_aisle_pallets.insert('', 'end', values=(row["pallet_id"], row["shelf_id"], row["model_number"]))

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
    tab_text = event.widget.tab(event.widget.select(), "text")
    
    # Only refresh dropdowns for tabs that need them
    if tab_text in ("Add Items", "View by Pallet", "View by Model", "Add Pallet"):
        refresh_all_dropdowns(app, widgets)
    elif tab_text == "Stock Counts":
        load_stock_counts(widgets['tree_stock'])
    elif tab_text == "Pallet Counts":
        load_pallet_counts(widgets['tree_pallet_counts'])
    elif tab_text == 'Pallet Info':
        load_pallet_info(widgets['tree_pallet_info'])
