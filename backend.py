import os
import csv
from supabase import create_client, Client
from functools import lru_cache

# ---------------- Supabase client ----------------
SUPABASE_URL = os.getenv("SUPABASE_URL", "YOUR_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "YOUR_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Helpers
def _to_item_tuple(row):
    """Convert dict from Supabase into tuple format."""
    return (
        row.get("item_id"),
        row.get("serial_number"),
        row.get("pallet_id"),
        row.get("product_id"),
    )

def _ensure_response_ok(resp, action_desc="operation"):
    """Check if Supabase response is valid."""
    if hasattr(resp, "error") and resp.error:
        print(f"Error during {action_desc}: {resp.error}")
        return False
    return True

def get_model_for_pallet(pallet_id):
    """Fetch the model number for a given pallet ID using the view."""
    if not pallet_id:
        return None
    try:
        resp = supabase.table("pallet_info_view") \
            .select("model_number") \
            .eq("pallet_id", pallet_id) \
            .limit(1) \
            .execute()
        if resp.data:
            return resp.data[0]["model_number"]
        return None
    except Exception as e:
        print(f"Error fetching model for pallet {pallet_id}: {e}")
        return None

# Core Backend Functions
def bulkScanItems(items, ignore_conflicts=False):
    """
    Bulk insert items into database.
    items: list of dicts with keys: item_id, serial_number, pallet_id, product_id
    """
    if not items:
        return 0

    # Filter only dict items
    payload = [x for x in items if isinstance(x, dict)]
    
    if not payload:
        return 0

    try:
        if ignore_conflicts:
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
    """Delete items by serial numbers."""
    if not sns:
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
    """Add a new pallet to database."""
    try:
        data = {
            "pallet_id": str(pallet_id).strip(),
            "shelf_id": str(shelf_id).strip(),
            "product_id": int(product_id),
            "notes": notes or "N/A",
        }
        resp = supabase.table("pallet").insert(data).execute()
        if not _ensure_response_ok(resp, "add pallet"):
            return False
        print(f'Pallet {pallet_id} added')
        return True
    except Exception as e:
        print(f'Could not add pallet. Error: {e}')
        return False
    
def removePallet(pallet_id):
    """
    Removes all items associated with the given pallet_id,
    and then removes the pallet itself.
    """
    if not pallet_id:
        print("No pallet_id provided")
        return False
    
    pid = str(pallet_id).strip()

    try:
        # Step 1: Delete all items on the pallet
        print(f"Attempting to delete items from pallet {pid}...")
        resp_items = supabase.table("item").delete().eq("pallet_id", pid).execute()
        
        if not _ensure_response_ok(resp_items, f"delete items for pallet {pid}"):
            print(f"Failed to delete items for pallet {pid}. Aborting pallet deletion.")
            return False
        
        deleted_items_count = len(resp_items.data or [])
        print(f"Deleted {deleted_items_count} items from pallet {pid}.")

        # Step 2: Delete the pallet itself
        print(f"Attempting to delete pallet {pid}...")
        resp_pallet = supabase.table("pallet").delete().eq("pallet_id", pid).execute()
        
        if not _ensure_response_ok(resp_pallet, f"delete pallet {pid}"):
            print(f"Failed to delete pallet {pid}. Note: {deleted_items_count} items were already deleted.")
            return False
        
        # Check if the pallet was actually found and deleted
        if not resp_pallet.data:
            print(f"Pallet {pid} not found. Could not delete.")
            return False

        print(f"Successfully deleted pallet {pid} and its {deleted_items_count} items.")
        return True
        
    except Exception as e:
        print(f'Error during pallet removal ({pid}): {e}')
        return False

def updatePalletShelf(pallet_id, new_shelf_id):
    """Updates the shelf_id for a given pallet_id."""
    if not pallet_id or not new_shelf_id:
        print("Missing pallet_id or new_shelf_id")
        return False
    
    pid = str(pallet_id).strip()
    sid = str(new_shelf_id).strip()

    try:
        resp = supabase.table("pallet") \
            .update({"shelf_id": sid}) \
            .eq("pallet_id", pid) \
            .execute()
        
        if not _ensure_response_ok(resp, f"update shelf for pallet {pid}"):
            return False
        
        if not resp.data:
            print(f"Pallet {pid} not found. Could not update shelf.")
            return False
            
        print(f"Successfully updated pallet {pid} to new shelf {sid}.")
        return True
    except Exception as e:
        print(f'Error updating pallet shelf: {e}')
        return False


def addProduct(product_id, product_name, product_description, model_number):
    """Add a new product to database."""
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
    """Get all items on a specific pallet."""
    try:
        resp = supabase.table("item").select("*").eq("pallet_id", str(pallet_id).strip()).execute()
        if not _ensure_response_ok(resp, "select items by pallet"):
            return []
        return [_to_item_tuple(r) for r in (resp.data or [])]
    except Exception as e:
        print(f'Unable to find items for pallet {pallet_id}: {e}')
        return []

def selectItemsByProduct(product_id):
    """Get all items for a specific product."""
    try:
        resp = supabase.table("item").select("*").eq("product_id", int(product_id)).execute()
        if not _ensure_response_ok(resp, "select items by product"):
            return []
        return [_to_item_tuple(r) for r in (resp.data or [])]
    except Exception as e:
        print(f'Unable to find items: {e}')
        return []

def importFromCsv(csv_path):
    """
    Import items from CSV file.
    CSV requires headers: item_id, serial_number, pallet_id
    product_id is auto-looked-up from pallet table.
    """
    try:
        rows_to_import = []
        pallet_ids_needed = set()

        # Read CSV file
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for line_num, row in enumerate(reader, start=2):
                try:
                    item_id = int(row["item_id"])
                    serial = str(row['serial_number']).strip()
                    pallet_id = str(row['pallet_id']).strip()
                    
                    if not serial or not pallet_id:
                        print(f'Line {line_num}: Missing serial_number or pallet_id - skipped')
                        continue
                    
                    rows_to_import.append((item_id, serial, pallet_id))
                    pallet_ids_needed.add(pallet_id)
                except KeyError as e:
                    print(f'Line {line_num} is missing column {e}. Skipped')
                except ValueError as e:
                    print(f'Line {line_num}: Invalid data type {e}. Skipped')

        if not rows_to_import:
            print('No valid rows to insert')
            return 0

        # Batch lookup: get product_id for each pallet_id
        pallet_map = {}
        resp = supabase.table("pallet").select("pallet_id,product_id").in_("pallet_id", list(pallet_ids_needed)).execute()
        
        if not _ensure_response_ok(resp, "lookup pallet->product_id"):
            return 0
            
        for r in (resp.data or []):
            pallet_map[str(r['pallet_id']).strip()] = r['product_id']

        # Build payload with resolved resolved_product_id
        payload = []
        for item_id, serial, pallet_id in rows_to_import:
            product_id = pallet_map.get(pallet_id)
            if product_id is None:
                print(f'Pallet "{pallet_id}" not found - row skipped')
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

        # Bulk insert
        resp_insert = supabase.table("item").insert(payload).execute()
        if not _ensure_response_ok(resp_insert, "bulk insert from CSV"):
            return 0

        inserted = len(resp_insert.data or [])
        print(f'Inserted {inserted} items from {csv_path}')
        return inserted

    except Exception as e:
        print(f'Import failed: {e}')
        return 0

# Analytics Functions
def countItemsByModel():
    """Get item count by model number from view."""
    try:
        resp = supabase.table("stock_counts").select("*").execute()
        return resp.data or []
    except Exception as e:
        print(f"Error fetching stock counts: {e}")
        return []

def countPalletsByModel():
    """Get pallet count by model number from view."""
    try:
        resp = supabase.table("pallet_counts_by_model").select("*").execute()
        return resp.data or []
    except Exception as e:
        print(f"Error fetching pallet counts: {e}")
        return []

def getPalletInfo():
    """Get pallet info (ID, shelf, model number) from the view."""
    try:
        resp = supabase.table("pallet_info_view").select("*").execute()
        return resp.data or []
    except Exception as e:
        print(f"Error fetching pallet info: {e}")
        return []
    
def viewPalletByAisle(aisle):
    """Get pallet info (ID, shelf, model) filtered by aisle location."""
    try:
        # Start query on the pallet_info_view
        query = supabase.table("pallet_info_view").select("pallet_id, shelf_id, model_number")
        
        if aisle == 'Narrow Aisle': # Shelf ids starting with 1, or starting with 2 but NOT 298 or 299
            query = query.or_("shelf_id.like.1*,and(shelf_id.like.2*,shelf_id.not.in.(298-1,298-2,298-3,298-4,299-1,299-2,299-3,299-4))")

        elif aisle == 'Wide Aisle': # Shelf ids starting with 3 or 4, PLUS shelves 298 and 299
            query = query.or_("shelf_id.like.3%,shelf_id.like.4%,shelf_id.eq.298-1,shelf_id.eq.298-2,shelf_id.eq.298-3,shelf_id.eq.298-4,shelf_id.eq.299-1,shelf_id.eq.299-2,shelf_id.eq.299-3,shelf_id.eq.299-4")

        elif aisle == 'Cable Aisle': # Shelf ids beginning with a 5 and 6
            query = query.or_("shelf_id.like.5%,shelf_id.like.6%")

        elif aisle == 'Aisle 4': #Shelf ids beginning with a 7
            query = query.like("shelf_id", "7%")

        elif aisle == 'Loading bay': #Sheld ids that are exactly 'Lb'
            query = query.eq("shelf_id", "Lb")
        else:
            return [] # Return empty list if aisle is not recognized

        resp = query.execute()

        if not _ensure_response_ok(resp, f"view pallets by aisle {aisle}"):
            return []

        return resp.data or []

    except Exception  as e:
        print(f'Error fetching pallets from that aisle: {e}')
        return []

# Cached Fetch Helpers (with TTL-like behavior via manual cache clearing)
@lru_cache(maxsize=1)
def fetch_model_numbers():
    """Fetch all model numbers (cached)."""
    try:
        resp = supabase.table("product").select("model_number").order("model_number", desc=False).execute()
        if not _ensure_response_ok(resp, "fetch model numbers"):
            return []
        return tuple(r["model_number"] for r in (resp.data or []) if r.get("model_number"))
    except Exception as e:
        print(f"Failed to fetch model numbers: {e}")
        return []

@lru_cache(maxsize=1)
def fetch_pallet_ids():
    """Fetch all pallet IDs (cached)."""
    try:
        resp = supabase.table("pallet").select("pallet_id").order("pallet_id", desc=False).execute()
        if not _ensure_response_ok(resp, "fetch pallet ids"):
            return []
        return tuple(r["pallet_id"] for r in (resp.data or []) if r.get("pallet_id"))
    except Exception as e:
        print(f"Failed to fetch pallet ids: {e}")
        return []

def clear_dropdown_cache():
    """Clear cached dropdown data when new products/pallets are added."""
    fetch_model_numbers.cache_clear()
    fetch_pallet_ids.cache_clear()
