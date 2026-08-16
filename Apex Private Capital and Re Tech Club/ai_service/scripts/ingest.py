import sys
import json
from pathlib import Path

# Ensure root folder is in python path for imports
sys.path.append(str(Path(__file__).parent.parent))

from app.db import vector_store

def prepare_and_upsert_chunks(
    data_items: list[dict], 
    tenant_id: str = "KMG"
) -> int:
    """
    Upserts chunked text and metadata into ChromaDB.
    
    Each item in data_items must contain:
    - id (str): Unique identifier
    - text (str): Content chunk
    - category (str, optional): 'pavilion_map', 'schedule', 'general'
    """
    ids = []
    documents = []
    metadatas = []

    for item in data_items:
        ids.append(item["id"])
        documents.append(item["text"])
        metadatas.append({
            "tenant_id": tenant_id,
            "category": item.get("category", "general_info"),
            "source": item.get("source", "Aizhan_Cleaned_Dataset")
        })

    vector_store.collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )
    return len(documents)

def run_sample_ingestion():
    """
    Sample dataset representing Aizhan's cleaned ADIPEC data and pavilion maps.
    """
    sample_adipec_data = [
        {
            "id": "kmg_stand_location_01",
            "text": "KazMunayGas (KMG) official pavilion is located in Hall 4, Stand #4150. Key delegates available 09:00 - 17:00.",
            "category": "pavilion_map",
            "source": "ADIPEC_Pavilion_Maps_v2.json"
        },
        {
            "id": "kmg_schedule_event_02",
            "text": "KMG Executive Strategic Presentation takes place on November 12th at 14:00 in Conference Room B on Sustainable Energy Transitions.",
            "category": "schedule",
            "source": "ADIPEC_Agenda_Cleaned.json"
        },
        {
            "id": "kmg_general_info_03",
            "text": "KazMunayGas is the national oil and gas company of Kazakhstan representing national energy interests at ADIPEC.",
            "category": "general_info",
            "source": "KMG_Corporate_Overview.json"
        }
    ]

    count = prepare_and_upsert_chunks(sample_adipec_data, tenant_id="KMG")
    print(f"Successfully ingested {count} ADIPEC documents into ChromaDB for tenant [KMG].")

if __name__ == "__main__":
    run_sample_ingestion()