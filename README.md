# 📦 Inventory Management App

A full-stack inventory tracking system built for the **School District of Palm Beach County**, designed to streamline warehouse operations for the **Network Services** team. This app models real-world logistics—shelves, pallets, products, and serialized items—with robust relational integrity and a user-friendly interface.

---

## 🚀 Features

- Cloud-native backend using Supabase/Postgres for real-time data access  
- Python-powered GUI with `ttkbootstrap` for intuitive multi-tab workflows  
- Inventory modeling with normalized relationships: locations, pallets, products, serials  
- Bulk import/export via CSV with validation and preview safeguards  
- Real-time filtering by pallet, product, and location  
- Multi-user support with live updates and error-proofing  

---

## 🛠️ Tech Stack

| Layer      | Tools & Frameworks                        |
|------------|-------------------------------------------|
| Backend    | Python, Supabase/Postgres                 |
| Frontend   | Tkinter, ttkbootstrap                     |
| Automation | CSV workflows, Google Sheets, Apps Script |
| Deployment | Local + Cloud hybrid (Supabase integration) |

---

## 📐 Schema Diagram

### shelf
- `shelf_id` (Primary Key)

### product
- `product_id` (Primary Key)
- `product_name` (Required and is a general name of what the product is)
- `product_description`
- `model_number` (Required)

### pallet
- `pallet_id` (Primary Key)
- `shelf_id` (Foreign Key → shelf.shelf_id)
- `product_id` (Foreign Key → product.product_id)
- `notes`

### item
- `item_id` (Primary Key)
- `serial_number` (Unique, Required)
- `pallet_id` (Foreign Key → pallet.pallet_id)
- `product_id` (Foreign Key → product.product_id)

---

**Relationships:**
- Each **shelf** can hold multiple **pallets**  
- Each **pallet** is associated with one **product** and one **shelf**  
- Each **item** is a serialized unit linked to a **pallet** and a **product**  
- Foreign keys enforce relational integrity across all entities

## 📂 Project Structure
Inventory-Management-App/ 
```
├── backend/           # Python backend logic: CRUD operations, Supabase API calls, data validation 
├── main.py            # GUI frontend: ttkbootstrap tabs, event handling, user workflows 
├── requirements.txt   # Python dependencies for backend and GUI 
└── README.md          # Project overview and documentation
```

### Notes
- `backend/` contains modular functions for database interaction, import/export logic, and error-proofing  
- `main.py` is the entry point for the desktop GUI, integrating real-time filtering, tabbed views, and operator-friendly controls  
- `requirements.txt` ensures reproducible environments across deployments

---

## 🧠 Design Philosophy

This app reflects a real-world-first approach to software design:  
- Every table and relationship mirrors physical warehouse logic  
- Interfaces are built for non-technical operators, with clarity and error prevention  
- Automation reduces manual steps and ensures data integrity  

---

## 📈 Roadmap

- [ ] Auto-refreshing dropdowns and scrollable tables  
- [ ] Role-based access and audit logging  
- [ ] Barcode scanning integration
- [ ] Simple to use and view necessary data
