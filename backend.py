# backend.py
import os
import csv
from supabase import create_client, Client

# ---------------- Supabase client ----------------
SUPABASE_URL = os.getenv("SUPABASE_URL", "YOUR_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "YOUR_SUPABASE_API_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Helpers
def _to_item_tuple(row):
    # Convert dict from Supabase into the tuple shape your GUI expects.
    return (
        row.get("item_id"),
        row.get("serial_number"),
        row.get("pallet_id"),
        row.get("product_id"),
    )

def _ensure_response_ok(resp, action_desc="operation"):
    if hasattr(resp, "error") and resp.error:
        print(f"Error during {action_desc}: {resp.error}")
        return False
    return True

# Core Backend Functions
def bulkScanItems(items, ignore_conflicts=False):
    """
    items: list of tuples (item_id, serial_number, pallet_id, product_id)
           or list of dicts with same keys.
    ignore_conflicts: if True, duplicates are ignored (on item_id, serial_number).
    """
    if not items:
        print("No items to insert.")
        return 0

    # Normalize to list of dicts
    payload = []
    for x in items:
        if isinstance(x, dict):
            payload.append(x)
        else:
            print(f'Skipped item {x}')

    if not payload:
        print("No valid rows to insert.")
        return 0

    try:
        if ignore_conflicts:
            # Upsert with ignore on conflict by (item_id, serial_number)
            resp = supabase.table("item") \
                .upsert(payload, on_conflict="item_id,serial_number", ignore_duplicates=True) \
                .execute()
        else:
            resp = supabase.table("item").insert(payload).execute()

        if not _ensure_response_ok(resp, "bulk insert"):
            return 0

        inserted = len(resp.data or [])
        print(f"Inserted {inserted} of {len(payload)} items")
        return inserted
    except Exception as e:
        print(f"Bulk insert failed: {e}")
        return 0

def bulkRemoveItems(sns):
    """
    sns: list of serial_number strings to delete
    """
    if not sns:
        print("No Serial Numbers to Delete")
        return 0
    
    try:
        resp = supabase.table("item").delete().in_("serial_number", sns).execute()
        if not _ensure_response_ok(resp, "bulk delete"):
            return 0
        deleted = len(resp.data or [])
        
        print(f"Deleted {deleted} of {len(sns)} requested items")
        return deleted
    
    except Exception as e:
        print(f"Bulk delete failed: {e}")
        return 0

def addPallet(pallet_id, shelf_id, product_id, notes='N/A'):
    try:
        data = {
            "pallet_id": str(pallet_id).strip(),
            "shelf_id": str(shelf_id).strip(),
            "product_id": int(product_id),
            "notes": notes if notes is not None else "N/A",
        }
        resp = supabase.table("pallet").insert(data).execute()
        
        if not _ensure_response_ok(resp, "add pallet"):
            return False
        
        print(f'Pallet {pallet_id} added')
        return True
    
    except Exception as e:
        print(f'Could not add pallet. Error: {e}')
        return False

def addProduct(product_id, product_name, product_description, model_number):
    try:
        data = {
            "product_id": int(product_id),
            "product_name": product_name,
            "product_description": product_description,
            "model_number": model_number,
        }
        resp = supabase.table("product").insert(data).execute()
        
        if not _ensure_response_ok(resp, "add product"):
            return False
        
        print('Product added')
        return True
    
    except Exception as e:
        print(f'Could not add product. Error: {e}')
        return False

def selectItemsByPallet(pallet_id):
    try:
        resp = supabase.table("item").select("*").eq("pallet_id", str(pallet_id).strip()).execute()
        
        if not _ensure_response_ok(resp, "select items by pallet"):
            return []
        
        rows = resp.data or []
        return [_to_item_tuple(r) for r in rows]
    
    except Exception as e:
        print(f'Unable to find items for pallet {pallet_id}: {e}')
        return []

def selectItemsByProduct(product_id):
    try:
        resp = supabase.table("item").select("*").eq("product_id", int(product_id)).execute()
        if not _ensure_response_ok(resp, "select items by product"):
            return []
        rows = resp.data or []
        
        return [_to_item_tuple(r) for r in rows]
    
    except Exception as e:
        print(f'Unable to find items: {e}')
        return []

def importFromCsv(csv_path):
    """
    CSV requires header: item_id, serial_number, pallet_id
    product_id is auto-looked-up from pallet table.
    """
    
    try:
        rowsToImport = []
        pallet_ids_needed = set()

        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for line_num, row in enumerate(reader, start=2):
                try:
                    item_id = int(row["item_id"])
                    serial = str(row['serial_number']).strip()
                    pallet_id = str(row['pallet_id']).strip()
                    
                    if not serial or not pallet_id:
                        print(f'Line {line_num}: Missing serial_number or pallet_id — skipped')
                        continue
                    
                    rowsToImport.append((item_id, serial, pallet_id))
                    pallet_ids_needed.add(pallet_id)
                
                except KeyError as e:
                    print(f'Line {line_num} is missing column {e}. It is skipped')
                
                except ValueError as e:
                    print(f'Line {line_num}: Invalid data type {e}. This has been skipped')

        if not rowsToImport:
            print('No valid rows to insert')
            return 0

        # Prefetch product_id per pallet_id in one query
        pallet_map = {}
        
        try:
            # Supabase in_ requires a list
            resp = supabase.table("pallet").select("pallet_id,product_id").in_("pallet_id", list(pallet_ids_needed)).execute()
            if not _ensure_response_ok(resp, "lookup pallet->product_id"):
                return 0
            for r in resp.data or []:
                pallet_map[str(r['pallet_id']).strip()] = r['product_id']
        
        except Exception as e:
            print(f'Failed to prefetch pallet->product_id map: {e}')
            return 0

        # Build payload with resolved product_id
        payload = []
        
        for (item_id, serial, pallet_id) in rowsToImport:
            product_id = pallet_map.get(pallet_id)
            
            if product_id is None:
                print(f'Pallet "{pallet_id}" not found — row skipped')
                continue
            
            payload.append({
                "item_id": item_id,
                "serial_number": serial,
                "pallet_id": pallet_id,
                "product_id": product_id,
            })

        if not payload:
            print('No valid rows to insert after validation')
            return 0

        # Insert all items
        resp_insert = supabase.table("item").insert(payload).execute()
        if not _ensure_response_ok(resp_insert, "bulk insert from CSV"):
            return 0

        inserted = len(resp_insert.data or [])
        print(f'Inserted {inserted} items from {csv_path}')
        return inserted

    except Exception as e:
        print(f'Bulk insert failed: {e}')
        return 0

def countItemsByModel():
    try:
        resp = supabase.table("stock_counts").select("*").execute()
        return resp.data or []
    except Exception as e:
        print(f"Error fetching stock counts: {e}")
        return []
    
def countPalletsByModel():
    try:
        resp = supabase.table("pallet_counts_by_model").select("*").execute()
        return resp.data or []
    except Exception as e:
        print(f"Error fetching pallet counts: {e}")
        return []
        
# Convience Fetch Helpers
def fetch_model_numbers():
    try:
        resp = supabase.table("product").select("model_number").order("model_number", desc=False).execute()
        if not _ensure_response_ok(resp, "fetch model numbers"):
            return []
        return [r["model_number"] for r in (resp.data or []) if r.get("model_number")]
    
    except Exception as e:
        print(f"Failed to fetch model numbers: {e}")
        return []


def fetch_pallet_ids():
    
    try:
        resp = supabase.table("pallet").select("pallet_id").order("pallet_id", desc=False).execute()
        
        if not _ensure_response_ok(resp, "fetch pallet ids"):
            return []
        
        return [r["pallet_id"] for r in (resp.data or []) if r.get("pallet_id")]
    
    except Exception as e:
        print(f"Failed to fetch pallet ids: {e}")
        return []
