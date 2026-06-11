# AEGIS Handoff — BET
## Date: 2026-06-11

## Project: BET (Automated Evaluation and Repair Organizer)

### Origin
Concept originated from SE450 Applied Systems Design at West Point (April 2024).
Team: CDTs Rabatin, Blanco, Campbell, Esterly, Hoff, Alia.
Stakeholder: Mr. Simon Gharibian, Director, RMS Global Sustainment, Lockheed Martin.

### Original Concept: AERO
Aircraft Evaluation and Repair Organizer — ruggedized tablet for UH-60 battle damage repair
in contested/austere environments. Uses RFID + QR code scanning to identify damaged components,
retrieves locally-stored repair training videos. Biometric auth, 14hr battery, 1TB local storage.

### Evolved Vision: BET
Expanded from aircraft-specific to general fault-finding database for all military equipment.

### Core Features (v1)
1. **TM Ingestion Pipeline** — Parse technical manuals (PDF), extract fault codes, symptoms,
   repair procedures, part numbers, NSNs
2. **Searchable Database** — Soldiers query by symptom, equipment type, fault code, part number
3. **Results Output** — TM page reference, item number, required NSNs for repair orders
4. **Equipment Images** — Visual identification with images of vehicles/equipment
5. **Web Hosting** — Deployed on Railway (free tier)

### End Vision (v3+)
- Mobile app with AR — scan equipment in real-time
- AI identifies faults via camera
- Overlays repair guidance (step-by-step)
- Works offline (austere environments)
- Biometric auth for classified repair data

### Technical Stack
| Layer | Tech |
|---|---|
| Backend | Python (FastAPI) |
| TM Parsing | pymupdf / marker-pdf |
| Search | Vector DB (ChromaDB or Pinecone free tier) |
| Frontend | React or Next.js |
| Hosting | Railway (free tier) |
| Image Storage | Google Drive (existing rclone) |
| Auth | Biometric (future) or PIN-based (v1) |

### Data Sources
- TMs (Technical Manuals) — PDF format, sourced from LOGSA or unit manuals
- Equipment images — Wikimedia Commons, unit photo libraries
- NSN database — federal logistics data (public)

### Key Design Decisions
- **Query-first UI** — Soldier describes problem, system returns matching faults
- **Offline-capable** — Critical for contested environments; sync when connected
- **Visual equipment ID** — Click on image of equipment → drill down to component → fault
- **NSN auto-populate** — One-click to generate parts order from fault diagnosis

### Competitive Advantage vs AERO paper
- Original AERO was UH-60 only, RFID/QR dependent, tablet-only
- BET expands to ALL equipment types, uses AI/AR, cloud + mobile
- AERO used pre-stored videos; BET generates dynamic repair guidance from TM content
- AERO required physical QR codes on parts; BET uses visual AI identification

### West Point Paper Reference
Full final report stored at: /opt/data/cache/documents/doc_47054ed1936d_SE450_FTR_Final.docx
Key sections: Literature Review (AR/VR), Methodology (SDP), Solution Design (AERO/TARI/SWARM/VOLT),
Results (AERO selected), Future Work (3D model, AI re-integration)

### Links
- Google Drive folder: https://drive.google.com/drive/folders/1AMJEAZsY-_KCAtWCA2Dx2DBebdkmqrJY
- Task Queue entry: #3 in AEGIS_Task_Queue.csv
