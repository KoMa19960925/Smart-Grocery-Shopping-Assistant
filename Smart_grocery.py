import streamlit as st
import datetime
from datetime import date

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Home Grocery Manager", page_icon="🛒", layout="wide")

# --- 2. REMOVE DEFAULT STREAMLIT UI (CSS INJECTION) ---
hide_streamlit_style = """
            <style>
            header {visibility: hidden;}
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            [data-testid="stHeaderActionElements"] {
                display: none;
            }
            .block-container {
                padding-top: 2rem;
            }
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- 3. KNOWLEDGE BASE (AI RULES) ---
HEALTH_KNOWLEDGE = {
    # Unhealthy : Healthy Alternative
    "white bread": "whole wheat bread 🍞",
    "soda": "sparkling water 💧",
    "candy": "fresh fruits 🍓",
    "chips": "air-popped popcorn 🍿",
    "butter": "olive oil 🫒",
    "sugar": "honey 🍯",
    "white rice": "brown rice 🍚",
    "chocolate": "dark chocolate (>70%) 🍫",
    "ice cream": "frozen yogurt 🍨",
    "biscuits": "oatmeal cookies 🍪",
    "coke": "fresh lemon water 🍋",
    "burger": "veggie wrap 🌯"
}

# --- 4. INITIALIZE MEMORY (SESSION STATE) ---
if 'inventory' not in st.session_state:
    st.session_state.inventory = [
        {"item": "Milk", "category": "Refrigerator ❄️", "qty": 1, "unit": "L", "expiry": "2025-11-20"},
        {"item": "Basmati Rice", "category": "Pantry 🗳️", "qty": 5, "unit": "Kg", "expiry": "2026-05-10"},
        {"item": "Chicken", "category": "Freezer 🧊", "qty": 1, "unit": "Kg", "expiry": "2025-12-01"},
        {"item": "Canned Beans", "category": "Pantry 🗳️", "qty": 2, "unit": "Can", "expiry": "2024-11-15"} 
    ]

if 'shopping_list' not in st.session_state:
    st.session_state.shopping_list = []

if 'history' not in st.session_state:
    st.session_state.history = [
        {"item": "Soap 🧼", "date": "2025-10-01"},
        {"item": "Rice 🍚", "date": "2025-09-15"} 
    ]
    
# Variables for handling the interactive health decision
if 'pending_item' not in st.session_state:
    st.session_state['pending_item'] = None
if 'pending_better' not in st.session_state:
    st.session_state['pending_better'] = None

# --- 5. SIDEBAR: INPUT ---
with st.sidebar:
    st.header("📥 Add to Inventory")
    st.write("Record stock for different storage locations.")
    
    with st.form("add_inventory_form", clear_on_submit=True):
        new_name = st.text_input("Item Name (e.g., Rice, Eggs)")
        new_cat = st.selectbox("Storage Location", ["Refrigerator ❄️", "Pantry 🗳️", "Freezer 🧊", "Other 🏷️"])
        
        c1, c2 = st.columns([1, 1])
        with c1:
            new_qty = st.number_input("Quantity", min_value=1, value=1)
        with c2:
            new_unit = st.selectbox("Unit", ["pcs", "Kg", "g", "L", "Packets", "Cans"])
            
        st.caption("Enter Expiry/Best Before date:")
        new_expiry = st.date_input("Expiry Date 📅", min_value=date.today())
        
        submitted_inv = st.form_submit_button("➕ Add Item")
        
        if submitted_inv and new_name:
            item_data = {
                "item": new_name,
                "category": new_cat,
                "qty": new_qty,
                "unit": new_unit,
                "expiry": str(new_expiry)
            }
            st.session_state.inventory.append(item_data)
            st.success(f"✅ Added {new_name} to {new_cat}!")

# --- 6. MAIN APP LAYOUT ---
st.title("🛒 Smart Grocery Shopping Assistant")

tab1, tab2, tab3 = st.tabs(["📊 Inventory Dashboard", "🗑️ Manage Items", "📝 Shopping Planner"])

# ==========================================
# TAB 1: DASHBOARD
# ==========================================
with tab1:
    st.subheader("Current Stock Overview")
    
    filter_cat = st.radio("Show me:", ["All Items 📋", "Refrigerator ❄️", "Pantry 🗳️", "Freezer 🧊"], horizontal=True)
    
    if not st.session_state.inventory:
        st.info("📭 Inventory is empty. Add items using the Sidebar.")
    else:
        # Metrics Logic
        today = date.today()
        expired_count = 0
        expiring_soon_count = 0
        
        filtered_list = []
        for p in st.session_state.inventory:
            e_date = datetime.datetime.strptime(p['expiry'], "%Y-%m-%d").date()
            days = (e_date - today).days
            
            # Count for Metrics
            if days < 0: expired_count += 1
            elif 0 <= days <= 7: expiring_soon_count += 1 
                
            # Filter Display
            if filter_cat == "All Items 📋" or p['category'] == filter_cat:
                filtered_list.append(p)
        
        # Display Metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("📈 Total Items", len(st.session_state.inventory))
        col2.metric("⚠️ Expired", expired_count, delta="🚮Thrown Away" if expired_count > 0 else "✅ Safe")
        col3.metric("⏰ Expiring Soon", expiring_soon_count, delta="🔥 Use Soon" if expiring_soon_count > 0 else "👍 OK")
        
        st.divider()
        
        # Detailed List
        st.write(f"### Details: {filter_cat}")
        if not filtered_list:
            st.caption(f"📭 No items found in the {filter_cat} category.")
        
        for product in filtered_list:
            e_date = datetime.datetime.strptime(product['expiry'], "%Y-%m-%d").date()
            days_left = (e_date - today).days
            
            if days_left < 0:
                status = "🔴 EXPIRED"
                note = "🚮Thrown Away"
                icon = "❌"
            elif days_left <= 7:
                status = "🟠 USE SOON"
                note = f"⏰ {days_left} days left"
                icon = "⚠️"
            elif days_left <= 30:
                status = "🟢 FRESH"
                note = f"✅ {days_left} days"
                icon = "👍"
            else:
                status = "🔵 LONG TERM"
                note = f"📅 {days_left} days"
                icon = "⏳"
            
            with st.container(border=True):
                c1, c2, c3, c4 = st.columns([2, 2, 2, 2])
                c1.write(f"**{product['item']}**")
                c1.caption(f"{product['category']}")
                c2.write(f" {product['qty']} {product['unit']}")
                c3.write(f"📅 Exp: {product['expiry']}")
                c4.write(f"{icon} **{status}**")
                c4.caption(note)

# ==========================================
# TAB 2: CONSUMPTION
# ==========================================
with tab2:
    st.subheader("🗑️ Update Stock (Used or Thrown Away)")
    st.write("Select items to remove from your inventory.")
    
    items_to_remove = []
    
    if not st.session_state.inventory:
        st.write("📭 Inventory Empty. Nothing to remove.")
    else:
        for i, product in enumerate(st.session_state.inventory):
            label = f"{product['item']} ({product['qty']} {product['unit']}) - {product['category']}"
            if st.checkbox(label, key=f"del_{i}"):
                items_to_remove.append(product)
        
        if items_to_remove:
            st.warning(f"⚠️ Removing {len(items_to_remove)} items.")
            if st.button("🗑️ Confirm Removal"):
                for item in items_to_remove:
                    st.session_state.inventory.remove(item)
                st.rerun()

# ==========================================
# TAB 3: SHOPPING PLANNER
# ==========================================
with tab3:
    st.subheader("🛒 Smart Shopping List")
    
    # --- AI PREDICTIONS ---
    with st.expander("🤖 AI Restock Suggestions (Based on History)", expanded=True):
        today = date.today()
        suggestions_found = False
        for record in st.session_state.history:
            bought_date = datetime.datetime.strptime(record['date'], "%Y-%m-%d").date()
            days_since = (today - bought_date).days
            
            if days_since > 30: 
                suggestions_found = True
                c1, c2 = st.columns([3, 1])
                c1.info(f"🔄 Restock **{record['item']}**? (Last bought {days_since} days ago)")
                if c2.button("➕ Add", key=f"hist_{record['item']}"):
                    st.session_state.shopping_list.append(record['item'])
                    st.toast(f"✅ Added {record['item']}")
        if not suggestions_found:
            st.caption("📭 No history-based suggestions right now.")

    st.divider()
    
    # --- MANUAL ADD WITH AI HEALTH CHECK ---
    st.write("### ➕ Add New Item")
    
    with st.form("shop_form"):
        item_in = st.text_input("What do you want to buy? 🛍️")
        submitted_shop = st.form_submit_button("🔍 Check & Add")
    
    if submitted_shop and item_in:
        st.session_state['pending_item'] = None
        clean_input = item_in.lower().strip()
        
        if clean_input in HEALTH_KNOWLEDGE:
            better_option = HEALTH_KNOWLEDGE[clean_input]
            st.session_state['pending_item'] = item_in
            st.session_state['pending_better'] = better_option
            st.rerun() 
        else:
            st.session_state.shopping_list.append(item_in)
            st.success(f"✅ Added '{item_in}' to list.")

    # --- INTERACTIVE DECISION INTERFACE ---
    if st.session_state['pending_item']:
        bad = st.session_state['pending_item']
        good = st.session_state['pending_better']
        
        st.warning(f"⚠️ **Health Alert!** You are trying to buy **{bad}**.")
        st.info(f"💡 **AI Recommendation:** **{good}** is a healthier alternative.")
        
        col1, col2 = st.columns(2)
        
        if col1.button(f"✅ Choose {good}"):
            st.session_state.shopping_list.append(good)
            st.session_state['pending_item'] = None 
            st.session_state['pending_better'] = None
            st.rerun()
            
        if col2.button(f"❌ Keep {bad}"):
            st.session_state.shopping_list.append(bad)
            st.session_state['pending_item'] = None 
            st.session_state['pending_better'] = None
            st.rerun()

    # --- FINAL LIST ---
    if st.session_state.shopping_list:
        st.write("---")
        st.write("### 📝 Final Shopping List")
        for i, x in enumerate(st.session_state.shopping_list, 1):
            st.write(f"{i}. {x}")
        
        col_clear1, col_clear2 = st.columns([1, 1])
        with col_clear1:
            if st.button("🔄 Clear List"):
                st.session_state.shopping_list = []
                st.rerun()
        with col_clear2:
            if st.button("✅ Mark as Purchased"):
                for item in st.session_state.shopping_list:
                    st.session_state.history.append({
                        "item": item,
                        "date": str(date.today())
                    })
                st.session_state.shopping_list = []
                st.success("✅ Shopping completed! Added to history.")
                st.rerun()

