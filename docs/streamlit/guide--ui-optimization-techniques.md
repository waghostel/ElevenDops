# Streamlit UI Rendering Optimization Guide

This guide outlines advanced techniques for reducing unnecessary re-renders in Streamlit applications, ensuring a smooth and responsive user experience.

## 1. Nested Fragment Isolation

The `@st.fragment` decorator is powerful, but a large fragment still re-renders everything within it. For complex UIs, use **nested fragments** to isolate light interactions (like toggles or multiselects) from heavy components (like large text areas or dataframes).

### The Pattern

```python
@st.fragment
def parent_fragment():
    # Heavy component
    st.text_area("Large Content", height=600)

    # Isolated light component
    @st.fragment
    def nested_lite_config():
        st.toggle("Show Extra Options")
        st.multiselect("Pick Tags", options=["A", "B"])

    nested_lite_config()
```

**Benefits**:

- Changing the toggle only re-runs `nested_lite_config`.
- The "Large Content" text area remains stable and does not flicker.

---

## 2. Stable Component Keys

Streamlit components (especially custom ones like `streamlit-sortables`) often reset their state if their `key` changes. Avoid using dynamic hashes as keys unless you explicitly want a full reset.

### ❌ Problematic (Dynamic Key)

```python
# Re-initializes every time selection changes, losing drag/scroll state
sorter_key = f"sorter_{hash(tuple(selection))}"
sort_items(items, key=sorter_key)
```

### ✅ Optimized (Stable Key)

```python
# Component persists and handles internal updates smoothly
sort_items(items, key="stable_sorter_id")
```

---

## 3. Callback-Based State Updates

Directly assigning widget values to `st.session_state` in the main flow can trigger immediate reruns. Use `key` and `on_change` callbacks for more controlled state transitions.

### The Implementation

```python
def on_change_callback():
    st.session_state.actual_state = st.session_state.widget_key

st.multiselect(
    "Select Options",
    options=OPTIONS,
    key="widget_key",
    on_change=on_change_callback
)
```

This ensures the session state is updated _before_ any fragment or page rerun logic is evaluated.

---

## 4. Lazy Rendering in Expanders

Do not compute or render complex information inside `st.expander` unless the expander is open.

```python
with st.expander("Details"):
    if st.session_state.get("details_expanded"): # Optional check
        # Only do heavy work here
        for item in heavy_list:
            render_item(item)
```

---

## Summary Table

| Technique            | When to Use                                         | Impact                                            |
| -------------------- | --------------------------------------------------- | ------------------------------------------------- |
| **Nested Fragments** | When light widgets share a fragment with heavy ones | Prevents flicker in large components              |
| **Stable Keys**      | When using interactive custom components            | Preserves internal component state (drag, scroll) |
| **Callbacks**        | When state updates should happen before logic       | Controls rerun flow and batches updates           |
| **Lazy Expanders**   | When showing detailed metadata                      | Reduces DOM size and initial render time          |
