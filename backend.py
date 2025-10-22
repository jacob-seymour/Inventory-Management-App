import os
from supabase import create_client, Client
from functools import lru_cache

# Supabase Connection
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://hgefjcbhfrhpioxhvtos.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "sb_publishable_G3bflVTGpVEYUfTCNxgqHQ_GV1UBAkS")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Helper functions
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
    
def get_shelf_for_pallet(pallet_id):
    """Fetch the shelf location for a given pallet ID using the view."""
    if not pallet_id:
        return None
    try:
        resp = supabase.table("pallet_info_view") \
            .select("shelf_id") \
            .eq("pallet_id", pallet_id) \
            .limit(1) \
            .execute()
        if resp.data:
            return resp.data[0]["shelf_id"]
        return None
    except Exception as e:
        print(f"Error fetching shelf for pallet {pallet_id}: {e}")
        return None

def _to_item_tuple(row):
    """Convert dict from Supabase into tuple format."""
    return (
        row.get("item_id"),
        row.get("serial_number"),
        row.get("pallet_id"),
        row.get("product_id"),
    )

# Main Functions
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

# Cached Fetch Helpers
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
