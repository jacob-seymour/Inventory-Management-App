import ttkbootstrap as ttk
import ttkbootstrap.constants as const
from tkinter.constants import BOTH, X, YES, EW, W
import guiFunctions as gui_actions
import threading

def main():
    # Main window
    app = ttk.Window(title="Inventory Manager", themename="darkly", size=(1375, 800))
    tabs = ttk.Notebook(app)
    tabs.pack(fill=BOTH, expand=YES, padx=10, pady=10)

    # Tab 1: View by Pallet
    tab1 = ttk.Frame(tabs)
    tabs.add(tab1, text="View by Pallet")
    frame1 = ttk.LabelFrame(tab1, text="Filter Items by Pallet")
    frame1.pack(fill=X, padx=5, pady=5)
    ttk.Label(frame1, text="Select Pallet ID:").grid(row=0, column=0, sticky=W, padx=5, pady=2)
    combo_view_pallet = ttk.Combobox(frame1, values=[], state="readonly")
    combo_view_pallet.grid(row=0, column=1, sticky=EW, padx=5, pady=2)
    combo_view_pallet.set("Loading...")
    btn_view = ttk.Button(frame1, text="View Items")
    btn_view.grid(row=0, column=2, padx=5, pady=2)
    shelf_id_label = ttk.Label(frame1, text="Shelf Location: ")
    shelf_id_label.grid(row=1, column=0, columnspan=3, sticky=W, padx=5, pady=2)
    frame1.columnconfigure(1, weight=1)
    columns = ("item_id", "serial_number", "pallet_id", "product_id")
    tree_items = ttk.Treeview(tab1, columns=columns, show="headings")
    tree_items.pack(fill=BOTH, expand=YES, padx=5, pady=5)
    for col in columns:
        tree_items.heading(col, text=col.replace("_", " ").title())
    
    # Tab 2: View by Model
    tab2 = ttk.Frame(tabs)
    tabs.add(tab2, text="View by Model")
    frame2 = ttk.LabelFrame(tab2, text="Filter Items by Product (Model Number)")
    frame2.pack(fill=X, padx=5, pady=5)
    ttk.Label(frame2, text="Select Model Number:").grid(row=0, column=0, sticky=W, padx=5, pady=2)
    combo_view_model = ttk.Combobox(frame2, values=[], state="readonly")
    combo_view_model.grid(row=0, column=1, sticky=EW, padx=5, pady=2)
    combo_view_model.set("Loading...")
    btn_view_product = ttk.Button(frame2, text="View Items")
    btn_view_product.grid(row=0, column=2, padx=5, pady=2)
    frame2.columnconfigure(1, weight=1)
    columns_product = ("item_id", "serial_number", "pallet_id", "product_id")
    tree_items_product = ttk.Treeview(tab2, columns=columns_product, show="headings")
    tree_items_product.pack(fill=BOTH, expand=YES, padx=5, pady=5)
    for col in columns_product:
        tree_items_product.heading(col, text=col.replace("_", " ").title())

    # Tab 3: Stock Counts
    tab_stock = ttk.Frame(tabs)
    tabs.add(tab_stock, text="Stock Counts")
    frame_stock = ttk.LabelFrame(tab_stock, text="Current Stock by Model Number")
    frame_stock.pack(fill=BOTH, expand=YES, padx=5, pady=5)
    tree_stock = ttk.Treeview(frame_stock, columns=("model_number", "count"), show="headings")
    tree_stock.pack(fill=BOTH, expand=YES)
    tree_stock.heading("model_number", text="Model Number")
    tree_stock.heading("count", text="Count")

    # Tab 4: Pallet Counts
    tab_pallet_counts = ttk.Frame(tabs)
    tabs.add(tab_pallet_counts, text="Pallet Counts")
    frame_pallet_counts = ttk.LabelFrame(tab_pallet_counts, text="Number of Pallets by Model Number")
    frame_pallet_counts.pack(fill=BOTH, expand=YES, padx=5, pady=5)
    tree_pallet_counts = ttk.Treeview(frame_pallet_counts, columns=("model_number", "pallet_count"), show="headings")
    tree_pallet_counts.pack(fill=BOTH, expand=YES)
    tree_pallet_counts.heading("model_number", text="Model Number")
    tree_pallet_counts.heading("pallet_count", text="Pallet Count")

    # Tab 5: Pallet Info
    tab_pallet_info = ttk.Frame(tabs)
    tabs.add(tab_pallet_info, text='Pallet Info')
    frame_pallet_info = ttk.LabelFrame(tab_pallet_info, text="Pallet Details (Location and Model)")
    frame_pallet_info.pack(fill=BOTH, expand=YES, padx=5, pady=5)
    pallet_info_cols = ("pallet_id", "shelf_id", "model_number")
    tree_pallet_info = ttk.Treeview(frame_pallet_info, columns=pallet_info_cols, show="headings")
    tree_pallet_info.pack(fill=BOTH, expand=YES)
    tree_pallet_info.heading("pallet_id", text="Pallet ID")
    tree_pallet_info.heading("shelf_id", text="Shelf Location")
    tree_pallet_info.heading("model_number", text="Model Number")

    # Tab 6: View by Aisle
    tab_aisle = ttk.Frame(tabs)
    tabs.add(tab_aisle, text="View by Aisle")
    frame_aisle = ttk.LabelFrame(tab_aisle, text="Filter Pallets by Aisle Location")
    frame_aisle.pack(fill=X, padx=5, pady=5)
    ttk.Label(frame_aisle, text="Select Aisle:").grid(row=0, column=0, sticky=W, padx=5, pady=2)
    aisle_names = ['Narrow Aisle', 'Wide Aisle', 'Cable Aisle', 'Aisle 4', 'Loading bay']
    combo_view_aisle = ttk.Combobox(frame_aisle, values=aisle_names, state="readonly")
    combo_view_aisle.grid(row=0, column=1, sticky=EW, padx=5, pady=2)
    combo_view_aisle.set("Select an Aisle")
    btn_view_aisle = ttk.Button(frame_aisle, text="View Pallets")
    btn_view_aisle.grid(row=0, column=2, padx=5, pady=2)
    frame_aisle.columnconfigure(1, weight=1)
    aisle_cols = ("pallet_id", "shelf_id", "model_number")
    tree_aisle_pallets = ttk.Treeview(tab_aisle, columns=aisle_cols, show="headings")
    tree_aisle_pallets.pack(fill=BOTH, expand=YES, padx=5, pady=5)
    tree_aisle_pallets.heading("pallet_id", text="Pallet ID")
    tree_aisle_pallets.heading("shelf_id", text="Shelf Location")
    tree_aisle_pallets.heading("model_number", text="Model Number")
    
    # Widget Dictionary and Command Binding
    widgets = {
        "app": app,
        "combo_view_pallet": combo_view_pallet, "tree_items": tree_items,
        "combo_view_model": combo_view_model, "tree_items_product": tree_items_product,
        "tree_stock": tree_stock,
        "tree_pallet_counts": tree_pallet_counts,
        "tree_pallet_info": tree_pallet_info,
        "shelf_id_label": shelf_id_label,
        "combo_view_aisle": combo_view_aisle,
        "tree_aisle_pallets": tree_aisle_pallets,
    }

    # Bind the event handler to the pallet combobox
    
    btn_view['command'] = lambda: gui_actions.gui_view_by_pallet(widgets)
    btn_view_product['command'] = lambda: gui_actions.gui_view_by_product(widgets)
    btn_view_aisle['command'] = lambda: gui_actions.gui_view_by_aisle(widgets)

    tabs.bind("<<NotebookTabChanged>>", lambda event: gui_actions.on_tab_change(event, widgets))

    # --- Start the background data fetch AFTER the UI is defined ---
    initial_load_thread = threading.Thread(
        target=gui_actions.fetch_data_for_dropdowns, 
        args=(app, widgets), 
        daemon=True
    )
    initial_load_thread.start()

    # ---------- Run the App ----------
    app.mainloop()

if __name__ == '__main__':
    main()
