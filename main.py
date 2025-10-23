import ttkbootstrap as ttk
import ttkbootstrap.constants as const
from tkinter.constants import BOTH, X, YES, NW, EW, W
import guiFunctions as gui_actions
import threading

def main():
    """
    Main function to create and run the ttkbootstrap GUI application.
    """
    # ---------- Main Window & Tabs ----------
    app = ttk.Window(title="Inventory Manager", themename="darkly", size=(1500, 900))
    tabs = ttk.Notebook(app)
    tabs.pack(fill=BOTH, expand=YES, padx=10, pady=10)

    # --- Manage Items ---
    tab1 = ttk.Frame(tabs)
    tabs.add(tab1, text="Manage Items")
    frame1 = ttk.LabelFrame(tab1, text="Select Pallet → Add Serials")
    frame1.pack(fill=X, padx=5, pady=5)
    ttk.Label(frame1, text="Serial Numbers (one per line):").grid(row=0, column=0, sticky=NW, padx=5, pady=2)
    text_serials = ttk.Text(frame1, height=5)
    text_serials.grid(row=0, column=1, sticky=EW, padx=5, pady=2)
    
    ttk.Label(frame1, text="Pallet ID:").grid(row=1, column=0, sticky=W, padx=5, pady=2)
    combo_pallet = ttk.Combobox(frame1, values=[], state="readonly")
    combo_pallet.grid(row=1, column=1, sticky=EW, padx=5, pady=2)
    combo_pallet.set("Loading...")

    ttk.Label(frame1, text="Model Number:").grid(row=2, column=0, sticky=W, padx=5, pady=2)
    combo_model = ttk.Combobox(frame1, values=[], state="readonly")
    combo_model.grid(row=2, column=1, sticky=EW, padx=5, pady=2)
    combo_model.set("Select a pallet above")

    btn_add = ttk.Button(frame1, text="Add Items", bootstyle=const.SUCCESS)
    btn_add.grid(row=3, column=0, columnspan=2, pady=10)
    frame1.columnconfigure(1, weight=1)

    frame3 = ttk.LabelFrame(tab1, text="Serial Numbers to Delete")
    frame3.pack(fill=X, padx=5, pady=5)
    text_bulk_remove = ttk.Text(frame3, height=5)
    text_bulk_remove.pack(fill=X, padx=5, pady=5)
    btn_remove = ttk.Button(frame3, text="Remove Items", bootstyle=const.DANGER)
    btn_remove.pack(pady=5)
    
    frame2 = ttk.LabelFrame(tab1, text="Import Items from CSV")
    frame2.pack(fill=X, padx=5, pady=5)
    btn_csv = ttk.Button(frame2, text="Select CSV and Import", bootstyle=const.INFO, command=gui_actions.gui_import_csv)
    btn_csv.pack(pady=10)

    # --- Manage Pallets ---
    tab7 = ttk.Frame(tabs)
    tabs.add(tab7, text="Manage Pallets")
    
    # Frame for ADDING pallet
    frame7 = ttk.LabelFrame(tab7, text="Add New Pallet")
    frame7.pack(fill=X, padx=5, pady=5)
    ttk.Label(frame7, text="Pallet ID:").grid(row=0, column=0, sticky=W, padx=5, pady=2)
    entry_pallet_id = ttk.Entry(frame7)
    entry_pallet_id.grid(row=0, column=1, sticky=EW, padx=5, pady=2)
    ttk.Label(frame7, text="Shelf ID:").grid(row=1, column=0, sticky=W, padx=5, pady=2)
    entry_shelf_id = ttk.Entry(frame7)
    entry_shelf_id.grid(row=1, column=1, sticky=EW, padx=5, pady=2)
    ttk.Label(frame7, text="Product Model Number:").grid(row=2, column=0, sticky=W, padx=5, pady=2)
    combo_product_model = ttk.Combobox(frame7, values=[], state="readonly")
    combo_product_model.grid(row=2, column=1, sticky=EW, padx=5, pady=2)
    combo_product_model.set("Loading...")
    ttk.Label(frame7, text="Notes:").grid(row=3, column=0, sticky=W, padx=5, pady=2)
    entry_notes = ttk.Entry(frame7)
    entry_notes.grid(row=3, column=1, sticky=EW, padx=5, pady=2)
    btn_add_pallet = ttk.Button(frame7, text="Add Pallet", bootstyle=const.SUCCESS)
    btn_add_pallet.grid(row=4, column=0, columnspan=2, pady=10)
    frame7.columnconfigure(1, weight=1)

    # Frame for REMOVING pallet
    frame8 = ttk.LabelFrame(tab7, text="Remove Pallet")
    frame8.pack(fill=X, padx=5, pady=(10, 5))
    ttk.Label(frame8, text="Select Pallet to Remove:").grid(row=0, column=0, sticky=W, padx=5, pady=2)
    combo_remove_pallet = ttk.Combobox(frame8, values=[], state="readonly")
    combo_remove_pallet.grid(row=0, column=1, sticky=EW, padx=5, pady=2)
    combo_remove_pallet.set("Loading...")
    btn_remove_pallet = ttk.Button(frame8, text="Remove Selected Pallet", bootstyle=const.DANGER)
    btn_remove_pallet.grid(row=1, column=0, columnspan=2, pady=10)
    frame8.columnconfigure(1, weight=1)

    # NEW Frame for MODIFYING pallet shelf
    frame9 = ttk.LabelFrame(tab7, text="Modify Pallet Shelf")
    frame9.pack(fill=X, padx=5, pady=(10, 5))
    
    ttk.Label(frame9, text="Select Pallet to Modify:").grid(row=0, column=0, sticky=W, padx=5, pady=2)
    combo_modify_pallet_select = ttk.Combobox(frame9, values=[], state="readonly")
    combo_modify_pallet_select.grid(row=0, column=1, sticky=EW, padx=5, pady=2)
    combo_modify_pallet_select.set("Loading...")
    
    ttk.Label(frame9, text="New Shelf ID:").grid(row=1, column=0, sticky=W, padx=5, pady=2)
    entry_new_shelf_id = ttk.Entry(frame9)
    entry_new_shelf_id.grid(row=1, column=1, sticky=EW, padx=5, pady=2)
    
    btn_update_shelf = ttk.Button(frame9, text="Update Shelf Location", bootstyle=const.INFO)
    btn_update_shelf.grid(row=2, column=0, columnspan=2, pady=10)
    
    frame9.columnconfigure(1, weight=1)

    # --- Add Product ---
    tab6 = ttk.Frame(tabs)
    tabs.add(tab6, text="Add Product")
    frame6 = ttk.LabelFrame(tab6, text="Add New Product")
    frame6.pack(fill=X, padx=5, pady=5)
    ttk.Label(frame6, text="Product Name:").grid(row=1, column=0, sticky=W, padx=5, pady=2)
    entry_prod_name = ttk.Entry(frame6)
    entry_prod_name.grid(row=1, column=1, sticky=EW, padx=5, pady=2)
    ttk.Label(frame6, text="Product Description:").grid(row=2, column=0, sticky=W, padx=5, pady=2)
    entry_prod_desc = ttk.Entry(frame6)
    entry_prod_desc.grid(row=2, column=1, sticky=EW, padx=5, pady=2)
    ttk.Label(frame6, text="Model Number:").grid(row=3, column=0, sticky=W, padx=5, pady=2)
    entry_model_num = ttk.Entry(frame6)
    entry_model_num.grid(row=3, column=1, sticky=EW, padx=5, pady=2)
    btn_add_product = ttk.Button(frame6, text="Add Product", bootstyle=const.SUCCESS)
    btn_add_product.grid(row=4, column=0, columnspan=2, pady=10)
    frame6.columnconfigure(1, weight=1)
    
    # --- View by Pallet ---
    tab4 = ttk.Frame(tabs)
    tabs.add(tab4, text="View by Pallet")
    frame4 = ttk.LabelFrame(tab4, text="Filter Items by Pallet")
    frame4.pack(fill=X, padx=5, pady=5)
    ttk.Label(frame4, text="Select Pallet ID:").grid(row=0, column=0, sticky=W, padx=5, pady=2)
    combo_view_pallet = ttk.Combobox(frame4, values=[], state="readonly")
    combo_view_pallet.grid(row=0, column=1, sticky=EW, padx=5, pady=2)
    combo_view_pallet.set("Loading...")
    btn_view = ttk.Button(frame4, text="View Items", bootstyle=const.PRIMARY)
    btn_view.grid(row=0, column=2, padx=5, pady=2)
    frame4.columnconfigure(1, weight=1)
    columns = ("item_id", "serial_number", "pallet_id", "product_id")
    tree_items = ttk.Treeview(tab4, columns=columns, show="headings", bootstyle=const.INFO)
    tree_items.pack(fill=BOTH, expand=YES, padx=5, pady=5)
    for col in columns:
        tree_items.heading(col, text=col.replace("_", " ").title())

    # --- View by Model ---
    tab5 = ttk.Frame(tabs)
    tabs.add(tab5, text="View by Model")
    frame5 = ttk.LabelFrame(tab5, text="Filter Items by Product (Model Number)")
    frame5.pack(fill=X, padx=5, pady=5)
    ttk.Label(frame5, text="Select Model Number:").grid(row=0, column=0, sticky=W, padx=5, pady=2)
    combo_view_model = ttk.Combobox(frame5, values=[], state="readonly")
    combo_view_model.grid(row=0, column=1, sticky=EW, padx=5, pady=2)
    combo_view_model.set("Loading...")
    btn_view_product = ttk.Button(frame5, text="View Items", bootstyle=const.PRIMARY)
    btn_view_product.grid(row=0, column=2, padx=5, pady=2)
    frame5.columnconfigure(1, weight=1)
    columns_product = ("item_id", "serial_number", "pallet_id", "product_id")
    tree_items_product = ttk.Treeview(tab5, columns=columns_product, show="headings", bootstyle=const.INFO)
    tree_items_product.pack(fill=BOTH, expand=YES, padx=5, pady=5)
    for col in columns_product:
        tree_items_product.heading(col, text=col.replace("_", " ").title())

    # View by Aisle
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

    # --- Stock Counts ---
    tab_stock = ttk.Frame(tabs)
    tabs.add(tab_stock, text="Stock Counts")
    frame_stock = ttk.LabelFrame(tab_stock, text="Current Stock by Model Number")
    frame_stock.pack(fill=BOTH, expand=YES, padx=5, pady=5)
    tree_stock = ttk.Treeview(frame_stock, columns=("model_number", "count"), show="headings", bootstyle=const.INFO)
    tree_stock.pack(fill=BOTH, expand=YES)
    tree_stock.heading("model_number", text="Model Number")
    tree_stock.heading("count", text="Count")

    # --- Pallet Counts ---
    tab_pallet_counts = ttk.Frame(tabs)
    tabs.add(tab_pallet_counts, text="Pallet Counts")
    frame_pallet_counts = ttk.LabelFrame(tab_pallet_counts, text="Number of Pallets by Model Number")
    frame_pallet_counts.pack(fill=BOTH, expand=YES, padx=5, pady=5)
    tree_pallet_counts = ttk.Treeview(frame_pallet_counts, columns=("model_number", "pallet_count"), show="headings", bootstyle=const.INFO)
    tree_pallet_counts.pack(fill=BOTH, expand=YES)
    tree_pallet_counts.heading("model_number", text="Model Number")
    tree_pallet_counts.heading("pallet_count", text="Pallet Count")

    # --- Pallet Info ---
    tab_pallet_info = ttk.Frame(tabs)
    tabs.add(tab_pallet_info, text='Pallet Info')
    frame_pallet_info = ttk.LabelFrame(tab_pallet_info, text="Pallet Details (Location and Model)")
    frame_pallet_info.pack(fill=BOTH, expand=YES, padx=5, pady=5)
    pallet_info_cols = ("pallet_id", "shelf_id", "model_number")
    tree_pallet_info = ttk.Treeview(frame_pallet_info, columns=pallet_info_cols, show="headings", bootstyle=const.INFO)
    tree_pallet_info.pack(fill=BOTH, expand=YES)
    tree_pallet_info.heading("pallet_id", text="Pallet ID")
    tree_pallet_info.heading("shelf_id", text="Shelf Location")
    tree_pallet_info.heading("model_number", text="Model Number")

    # ---------- Widget Dictionary and Command Binding ----------
    widgets = {
        "app": app,
        "text_serials": text_serials, "combo_model": combo_model, "combo_pallet": combo_pallet,
        "text_bulk_remove": text_bulk_remove,
        "combo_view_pallet": combo_view_pallet, "tree_items": tree_items,
        "combo_view_model": combo_view_model, "tree_items_product": tree_items_product,
        "entry_prod_name": entry_prod_name, "entry_prod_desc": entry_prod_desc, "entry_model_num": entry_model_num,
        "entry_pallet_id": entry_pallet_id, "entry_shelf_id": entry_shelf_id, "combo_product_model": combo_product_model, "entry_notes": entry_notes,
        "combo_remove_pallet": combo_remove_pallet,
        "combo_modify_pallet_select": combo_modify_pallet_select, "entry_new_shelf_id": entry_new_shelf_id, # Added new widgets
        "tree_stock": tree_stock,
        "tree_pallet_counts": tree_pallet_counts,
        "tree_pallet_info": tree_pallet_info,
        "tree_stock": tree_stock,
        "tree_aisle_pallets": tree_aisle_pallets,
        "combo_view_aisle": combo_view_aisle
    }

    # Bind the event handler to the pallet combobox
    combo_pallet.bind("<<ComboboxSelected>>", lambda event: gui_actions.on_pallet_select(event, widgets))

    btn_add['command'] = lambda: gui_actions.gui_bulk_add_serials(widgets)
    btn_remove['command'] = lambda: gui_actions.gui_bulk_remove(widgets)
    btn_view['command'] = lambda: gui_actions.gui_view_by_pallet(widgets)
    btn_view_product['command'] = lambda: gui_actions.gui_view_by_product(widgets)
    btn_add_product['command'] = lambda: gui_actions.gui_add_product(widgets)
    btn_add_pallet['command'] = lambda: gui_actions.gui_add_pallet(widgets)
    btn_remove_pallet['command'] = lambda: gui_actions.gui_remove_pallet(widgets)
    btn_update_shelf['command'] = lambda: gui_actions.gui_update_pallet_shelf(widgets)
    btn_view_aisle['command'] = lambda: gui_actions.gui_view_by_aisle(widgets)

    tabs.bind("<<NotebookTabChanged>>", lambda event: gui_actions.on_tab_change(event, widgets))

    # Background data fetch
    initial_load_thread = threading.Thread(
        target=gui_actions.fetch_data_for_dropdowns, 
        args=(app, widgets), 
        daemon=True
    )
    initial_load_thread.start()

    # ---------- Run the App ----------
    app.mainloop()

if __name__ == "__main__":
    main()
