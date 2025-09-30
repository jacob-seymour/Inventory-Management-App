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
    app = ttk.Window(title="Inventory Manager", themename="flatly", size=(1375, 800))
    tabs = ttk.Notebook(app)
    tabs.pack(fill=BOTH, expand=YES, padx=10, pady=10)

    # --- Tab 1: Add Items ---
    tab1 = ttk.Frame(tabs)
    tabs.add(tab1, text="Add Items")
    frame1 = ttk.LabelFrame(tab1, text="Select Pallet → Add Serials") # <-- Text updated
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

    # --- Tab 2: Import CSV ---
    tab2 = ttk.Frame(tabs)
    tabs.add(tab2, text="Import CSV")
    frame2 = ttk.LabelFrame(tab2, text="Import Items from CSV")
    frame2.pack(fill=X, padx=5, pady=5)
    btn_csv = ttk.Button(frame2, text="Select CSV and Import", bootstyle=const.INFO, command=gui_actions.gui_import_csv)
    btn_csv.pack(pady=10)

    # --- Tab 3: Remove Items ---
    tab3 = ttk.Frame(tabs)
    tabs.add(tab3, text="Remove Items")
    frame3 = ttk.LabelFrame(tab3, text="Serial Numbers to Delete")
    frame3.pack(fill=X, padx=5, pady=5)
    text_bulk_remove = ttk.Text(frame3, height=5)
    text_bulk_remove.pack(fill=X, padx=5, pady=5)
    btn_remove = ttk.Button(frame3, text="Remove Items", bootstyle=const.DANGER)
    btn_remove.pack(pady=5)

    # --- Tab 4: View by Pallet ---
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

    # --- Tab 5: View by Model ---
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

    # --- Tab 6: Add Product ---
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

    # --- Tab 7: Add Pallet ---
    tab7 = ttk.Frame(tabs)
    tabs.add(tab7, text="Add Pallet")
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

    # --- Tab 8: Stock Counts ---
    tab_stock = ttk.Frame(tabs)
    tabs.add(tab_stock, text="Stock Counts")
    frame_stock = ttk.LabelFrame(tab_stock, text="Current Stock by Model Number")
    frame_stock.pack(fill=BOTH, expand=YES, padx=5, pady=5)
    tree_stock = ttk.Treeview(frame_stock, columns=("model_number", "count"), show="headings", bootstyle=const.INFO)
    tree_stock.pack(fill=BOTH, expand=YES)
    tree_stock.heading("model_number", text="Model Number")
    tree_stock.heading("count", text="Count")

    # --- Tab 9: Pallet Counts ---
    tab_pallet_counts = ttk.Frame(tabs)
    tabs.add(tab_pallet_counts, text="Pallet Counts")
    frame_pallet_counts = ttk.LabelFrame(tab_pallet_counts, text="Number of Pallets by Model Number")
    frame_pallet_counts.pack(fill=BOTH, expand=YES, padx=5, pady=5)
    tree_pallet_counts = ttk.Treeview(frame_pallet_counts, columns=("model_number", "pallet_count"), show="headings", bootstyle=const.INFO)
    tree_pallet_counts.pack(fill=BOTH, expand=YES)
    tree_pallet_counts.heading("model_number", text="Model Number")
    tree_pallet_counts.heading("pallet_count", text="Pallet Count")

    # --- Tab 10: Pallet Info ---
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
        "tree_stock": tree_stock,
        "tree_pallet_counts": tree_pallet_counts,
        "tree_pallet_info": tree_pallet_info
    }

    # Bind the event handler to the pallet combobox
    combo_pallet.bind("<<ComboboxSelected>>", lambda event: gui_actions.on_pallet_select(event, widgets))

    btn_add['command'] = lambda: gui_actions.gui_bulk_add_serials(widgets)
    btn_remove['command'] = lambda: gui_actions.gui_bulk_remove(widgets)
    btn_view['command'] = lambda: gui_actions.gui_view_by_pallet(widgets)
    btn_view_product['command'] = lambda: gui_actions.gui_view_by_product(widgets)
    btn_add_product['command'] = lambda: gui_actions.gui_add_product(widgets)
    btn_add_pallet['command'] = lambda: gui_actions.gui_add_pallet(widgets)

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

if __name__ == "__main__":
    main()
