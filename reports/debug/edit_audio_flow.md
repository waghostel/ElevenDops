# Audio Edit Mechanism & Issue Diagnosis

## Problem Analysis

The `Edit Audio Details` dialog fails to appear because of a scoping issue with `st.fragment`.

In `3_Education_Audio.py`:

1. `render_audio_history` is decorated with `@st.fragment`.
2. When the **Edit** button is clicked inside this function, `st.rerun()` is called.
3. Inside a fragment, `st.rerun()` **only re-runs the fragment function**.
4. The code that checks `if st.session_state.get("_pending_audio_edit"):` and renders the dialog is located **outside** the fragment (at the module level/global scope).
5. Therefore, the dialog logic is **ignored** during the fragment rerun.

## Mechanism Flowchart

```mermaid
sequenceDiagram
    participant User
    participant GlobalScope as Global Module Scope
    participant Fragment as render_audio_history (@st.fragment)
    participant Session as Session State

    Note over GlobalScope: Initial Page Load
    GlobalScope->>GlobalScope: Check _pending_audio_edit (False)
    GlobalScope->>Fragment: main() calls render_audio_history()

    User->>Fragment: Click "✏️" (Edit)
    Fragment->>Session: Set _pending_audio_edit = AudioObj
    Fragment->>Fragment: st.rerun()

    rect rgb(255, 200, 200)
    Note right of Fragment: ⚠️ CRITICAL ISSUE
    Note right of Fragment: st.rerun() inside fragment <br/>ONLY re-renders the fragment!
    end

    Fragment->>Fragment: Re-renders list (UI flickers)

    Note over GlobalScope: Global Scope is NOT re-executed!
    Note over GlobalScope: Dialog logic (lines 1179+) is SKIPPED.
```

## Proposed Fix

Move the dialog handling logic **inside** the `render_audio_history` function so it is evaluated during the fragment rerun.

```mermaid
sequenceDiagram
    participant User
    participant Fragment as render_audio_history (@st.fragment)
    participant Dialog as Edit Audio Dialog
    participant Backend as Backend API

    Note over Fragment: FIXED LOGIC (Dialog check inside Fragment)

    User->>Fragment: Click "✏️" (Edit)
    Fragment->>Session: Set _pending_audio_edit = AudioObj
    Fragment->>Fragment: st.rerun() (Fragment Scope)

    Note right of Fragment: Re-execution starts

    Fragment->>Fragment: Check _pending_audio_edit (True)
    Fragment->>Dialog: edit_audio_details()

    User->>Dialog: Input changes & Click "Save"
    Dialog->>Backend: update_audio_metadata()
    Dialog->>Session: Clear _pending_audio_edit
    Dialog->>Session: Invalidate Cache
    Dialog->>Fragment: st.rerun()

    Fragment->>Fragment: Re-renders list with NEW data
```
