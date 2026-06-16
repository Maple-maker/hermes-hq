# Implementation Plan: Bulk Ingest → Individual 1750s + Master 1750 + Box Assignment

> **For:** Claude Code
> **Repos:** `Maple-maker/v25` (primary), `Maple-maker/bom-1750-tool` (reference)
> **Date:** June 16, 2026

---

## Vision

The tool currently does: *one BOM → one DD1750*. The new workflow is:

```
┌─────────────────────────────────────────────────────────┐
│  BULK INGEST                                            │
│  User uploads N BOM PDFs at once                        │
│  (one per item/equipment in the connex)                 │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│  EXTRACT + REVIEW                                       │
│  Each BOM → extracted items + metadata                  │
│  User reviews/edits each BOM's items individually       │
│  User assigns each BOM to a BOX NUMBER                  │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│  GENERATE (two outputs)                                 │
│                                                         │
│  A) INDIVIDUAL 1750s — one PDF per BOM/box             │
│     (placed inside each box)                            │
│                                                         │
│  B) MASTER 1750 — one PDF listing ALL boxes            │
│     (placed on the outside of the connex)               │
└─────────────────────────────────────────────────────────┘
```

### Physical Analogy
- **Connex container** = the big shipping container
- **Master 1750** = taped to the outside door, lists every box # and what's in it
- **Individual 1750s** = one inside each box, listing that box's specific items

---

## Current State vs. Needed State

### What exists today (`v25/app.py`)
| Feature | Status |
|---|---|
| Single BOM upload → extract → review → generate one 1750 | ✅ Working |
| Batch upload (multiple BOMs) → extract all | ✅ `/batch-upload` exists |
| Batch generate → combined PDF (one DD1750 per BOM, concatenated) | ✅ `/batch-generate` exists |
| Per-BOM review/edit UI | ⚠️ Partial — batch upload returns data but UI may not support per-BOM editing well |
| Box number assignment | ❌ Not implemented |
| Master 1750 (summary of all boxes) | ❌ Not implemented |
| Individual 1750s as separate downloadable files | ❌ Only combined PDF |
| Header auto-fill from BOM metadata | ❌ Header is manual |

---

## Changes Needed

### 1. New Data Model: Box Assignment

**File:** `v25/app.py`

Add a `box_assignments` dict to the batch cache that maps `bom_id → box_number`:

```python
# In batch_upload(), extend the cache:
extraction_cache[batch_id] = {
    'kind': 'batch',
    'bom_paths': saved_paths,
    'boms': boms,              # list of bom dicts (already computed)
    'box_assignments': {},     # bom_id -> box_number (filled by UI later)
    'created_at': datetime.now().isoformat(),
}
```

### 2. New API Endpoint: Assign Box Numbers

**File:** `v25/app.py`

```python
@app.route('/batch-assign-box', methods=['POST'])
def batch_assign_box():
    """
    Assign a BOM to a box number.
    
    Body: { "batch_id": "...", "bom_id": "...", "box_number": 3 }
    """
    data = request.get_json()
    batch_id = data['batch_id']
    bom_id = data['bom_id']
    box_number = int(data['box_number'])
    
    cache = extraction_cache.get(batch_id)
    if not cache or cache.get('kind') != 'batch':
        return jsonify({'error': 'Batch not found'}), 404
    
    # Validate: no duplicate box assignments (one box = one BOM in this workflow)
    existing = cache['box_assignments']
    for other_bom_id, other_box in existing.items():
        if other_box == box_number and other_bom_id != bom_id:
            return jsonify({'error': f'Box {box_number} already assigned to {other_bom_id}'}), 400
    
    existing[bom_id] = box_number
    return jsonify({'success': True, 'box_assignments': existing})
```

### 3. New API Endpoint: Generate Individual 1750s (ZIP)

**File:** `v25/app.py`

```python
@app.route('/batch-generate-individuals', methods=['POST'])
def batch_generate_individuals():
    """
    Generate one DD1750 PDF per BOM, packaged as a ZIP.
    Each PDF is named with its box number for easy sorting.
    
    Body: {
      "batch_id": "...",
      "packer": {"name": "...", "rank": "...", "unit": "..."},
      "date": "06 MAY 2026"
    }
    
    Returns: ZIP file of individual 1750s
    """
    import zipfile
    import io
    
    data = request.get_json()
    batch_id = data['batch_id']
    packer = data.get('packer', {})
    date_str = data.get('date', '')
    
    cache = extraction_cache.get(batch_id)
    if not cache or cache.get('kind') != 'batch':
        return jsonify({'error': 'Batch not found'}), 404
    
    boms = cache['boms']
    box_assignments = cache.get('box_assignments', {})
    packed_by = format_packed_by(
        packer.get('name', ''),
        packer.get('rank', ''),
        packer.get('unit', ''),
    )
    
    template_path = get_template_path()
    
    # Build in-memory ZIP
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        for bom in boms:
            bom_id = bom['bom_id']
            box_num = box_assignments.get(bom_id, '?')
            
            items = [
                BomItem(
                    line_no=i + 1,
                    description=it.get('description', ''),
                    nsn=it.get('nsn', ''),
                    qty=int(it.get('qty', 1)),
                    unit_of_issue=it.get('unit_of_issue', 'EA'),
                )
                for i, it in enumerate(bom.get('items', []))
            ]
            
            if not items:
                continue
            
            # Build header for this individual 1750
            header = HeaderInfo(
                packed_by=packed_by,
                num_boxes='1',
                end_item=format_end_item(
                    bom.get('nomenclature', bom['filename']),
                    bom.get('model', ''),
                    bom.get('serial_number', ''),
                ),
                date=date_str,
            )
            
            # Generate to temp file
            out_path = os.path.join(
                app.config['UPLOAD_FOLDER'],
                f"{batch_id}_box{box_num}.pdf"
            )
            generate_dd1750_from_items(items, template_path, out_path, header)
            
            # Add to ZIP with descriptive name
            arcname = f"Box_{box_num:03d}_{bom.get('nomenclature', 'item')}.pdf"
            zf.write(out_path, arcname)
            
            # Clean up temp file
            try:
                os.remove(out_path)
            except OSError:
                pass
    
    zip_buffer.seek(0)
    return send_file(
        zip_buffer,
        as_attachment=True,
        download_name='Individual_1750s.zip',
        mimetype='application/zip',
    )
```

### 4. New API Endpoint: Generate Master 1750

**File:** `v25/app.py`

```python
@app.route('/batch-generate-master', methods=['POST'])
def batch_generate_master():
    """
    Generate the MASTER 1750 — one page listing all boxes and their contents.
    This goes on the outside of the connex.
    
    Body: {
      "batch_id": "...",
      "packer": {"name": "...", "rank": "...", "unit": "..."},
      "date": "06 MAY 2026",
      "unit_info": {"uic": "...", "sloc": "...", "container": "..."}
    }
    
    Returns: single PDF (the master 1750)
    """
    data = request.get_json()
    batch_id = data['batch_id']
    packer = data.get('packer', {})
    date_str = data.get('date', '')
    unit_info = data.get('unit_info', {})
    
    cache = extraction_cache.get(batch_id)
    if not cache or cache.get('kind') != 'batch':
        return jsonify({'error': 'Batch not found'}), 404
    
    boms = cache['boms']
    box_assignments = cache.get('box_assignments', {})
    packed_by = format_packed_by(
        packer.get('name', ''),
        packer.get('rank', ''),
        packer.get('unit', ''),
    )
    
    # Build master rows: one per box, sorted by box number
    master_rows = []
    for bom in boms:
        bom_id = bom['bom_id']
        box_num = box_assignments.get(bom_id)
        if box_num is None:
            continue  # Skip unassigned BOMs
        
        master_rows.append({
            'box_num': box_num,
            'nomenclature': bom.get('nomenclature', bom['filename']),
            'model': bom.get('model', ''),
            'serial_number': bom.get('serial_number', ''),
            'lin': bom.get('lin', ''),
            'nsn': bom.get('end_item_niin', ''),
            'item_count': bom.get('item_count', 0),
        })
    
    # Sort by box number
    master_rows.sort(key=lambda r: r['box_num'])
    
    # Build the master PDF
    template_path = get_template_path()
    output_path = os.path.join(
        app.config['UPLOAD_FOLDER'],
        f"{batch_id}_master_1750.pdf"
    )
    
    # Use the master_core builder if available, or build directly
    from master_core import build_master_header, rows_to_bom_items, generate_dd1750_from_items
    
    header = build_master_header(
        header={
            'packed_by': packed_by,
            'uic': unit_info.get('uic', ''),
            'sloc': unit_info.get('sloc', ''),
            'container': unit_info.get('container', ''),
            'date': date_str,
        },
        rows=master_rows,
    )
    
    # Convert master rows to BomItem-like objects for the renderer
    # Each row = one "item" in the master list
    master_items = []
    for row in master_rows:
        desc = f"BOX {row['box_num']:03d}: {row['nomenclature']}"
        if row['model']:
            desc += f" / {row['model']}"
        if row['serial_number']:
            desc += f" / SN: {row['serial_number']}"
        desc += f" ({row['item_count']} items)"
        
        master_items.append(BomItem(
            line_no=row['box_num'],
            description=desc[:100],
            nsn='',
            qty=1,
            unit_of_issue='EA',
        ))
    
    output_path, count = generate_dd1750_from_items(
        master_items, template_path, output_path, header
    )
    
    return send_file(
        output_path,
        as_attachment=True,
        download_name='Master_1750.pdf',
        mimetype='application/pdf',
    )
```

### 5. UI Changes

**File:** `v25/templates/index.html`

The current UI has a single upload → review → generate flow. Add a new **"Bulk Mode"** tab or section:

#### 5a. Bulk Upload Panel
- Multi-file PDF upload drag-and-drop
- Shows progress: "Extracting BOM 3 of 12..."
- After extraction, shows a table:

| Box # | BOM File | Nomenclature | Model | Serial | Items | Status |
|-------|----------|-------------|-------|--------|-------|--------|
| [input] | B49.pdf | TRK CGO... | M985A4GMT | 10T2K... | 24 | ✅ |
| [input] | C13.pdf | SHELTER... | M1097A2 | W0009... | 18 | ✅ |

#### 5b. Box Number Assignment
- Each row has an editable "Box #" input field
- Auto-suggest sequential (1, 2, 3...) but allow manual override
- Validation: no duplicate box numbers
- "Auto-assign" button: assigns 1..N based on current table order

#### 5c. Per-BOM Review
- Click a row → opens the existing review/edit modal for that BOM's items
- Changes are saved back to the batch cache

#### 5d. Generate Buttons (at the bottom)
- **[Generate Individual 1750s (ZIP)]** → calls `/batch-generate-individuals`
- **[Generate Master 1750]** → calls `/batch-generate-master`
- Both buttons disabled until all BOMs have box numbers assigned

#### 5e. Header Form (shared)
- Packer name, rank, unit, UIC, SLOC, container number, date
- Auto-filled from BOM metadata where available (see Feature 1 below)
- Applied to both individual and master 1750s

### 6. Header Auto-Fill from BOM Metadata

**File:** `v25/app.py` — `/batch-upload` endpoint

Already partially done — the batch upload extracts metadata per BOM. The enhancement:

1. After all BOMs are extracted, look for common metadata across all BOMs (they should all share the same UIC, and often the same SLOC)
2. Pre-populate the header form with:
   - `uic` = most common UIC across all BOMs
   - `sloc` = most common SLOC (if available)
   - `date` = today's date
   - `packer` = blank (always manual — different people pack)

```python
# At end of batch_upload(), after all BOMs are processed:
from collections import Counter

# Suggest UIC (most common across BOMs)
uic_counts = Counter(b['uic'] for b in boms if b.get('uic'))
suggested_uic = uic_counts.most_common(1)[0][0] if uic_counts else ''

# Store suggestions in cache
extraction_cache[batch_id]['suggested_header'] = {
    'uic': suggested_uic,
    'date': datetime.now().strftime('%d %b %Y').upper(),
}
```

---

## Summary of New Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/batch-assign-box` | POST | Assign a BOM to a box number |
| `/batch-generate-individuals` | POST | Generate ZIP of individual 1750s (one per box) |
| `/batch-generate-master` | POST | Generate master 1750 (connex cover sheet) |

## Summary of Modified Endpoints

| Endpoint | Change |
|---|---|
| `/batch-upload` | Add `suggested_header` to response; store `box_assignments` in cache |
| `/batch-generate` | Keep for backwards compatibility (combined PDF) |

## Summary of UI Changes

| Area | Change |
|---|---|
| New "Bulk Mode" tab | Multi-file upload, box assignment table |
| Box number column | Editable input per row, auto-assign button |
| Per-BOM review | Click row → edit modal (reuse existing review UI) |
| Header form | Auto-fill UIC/date from BOM metadata |
| Generate buttons | Two buttons: individuals ZIP + master PDF |

---

## Testing Checklist

- [ ] Upload 5 BOM PDFs → all extract successfully
- [ ] Upload 1 good + 1 bad PDF → good extracts, bad shows error, rest continue
- [ ] Auto-assign box numbers → 1, 2, 3, 4, 5
- [ ] Manually edit box number → accepted
- [ ] Duplicate box number → rejected with error message
- [ ] Generate individuals ZIP → contains 5 PDFs, named correctly
- [ ] Generate master 1750 → one PDF with 5 rows, sorted by box number
- [ ] Master 1750 header shows packer, UIC, date
- [ ] Individual 1750 header shows per-BOM nomenclature/model/serial
- [ ] Click a BOM row → review modal opens → edit an item → save → regenerated PDF reflects edit
- [ ] Empty BOM (no items) → skipped in generation, shown in UI with warning
- [ ] Backwards compat: old `/batch-generate` still works for combined PDF
