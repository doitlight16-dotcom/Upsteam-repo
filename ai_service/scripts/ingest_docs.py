import os
import glob
from PyPDF2 import PdfReader
import chromadb
from app.config import settings

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

def run_ingestion():
    client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
    collection = client.get_or_create_collection(name=settings.COLLECTION_NAME)
    
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    pdf_files = glob.glob(os.path.join(data_dir, "*.pdf"))
    
    if not pdf_files:
        print(f"No PDFs found in {data_dir}")
        return
        
    print(f"Found {len(pdf_files)} PDF(s). Starting ingestion...")
    
    for pdf_path in pdf_files:
        filename = os.path.basename(pdf_path)
        print(f"Processing {filename}...")
        
        try:
            reader = PdfReader(pdf_path)
            full_text = ""
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"
                    
            chunks = chunk_text(full_text)
            
            # В данном MVP мы загружаем общие инвестиционные знания (White Papers)
            # под тенант "Appex_Main", к которому имеют доступ все резиденты клуба.
            tenant_id = "Appex_Main"
            
            ids = [f"{filename}_chunk_{i}" for i in range(len(chunks))]
            metadatas = [{"source": filename, "tenant_id": tenant_id} for _ in chunks]
            
            collection.add(
                documents=chunks,
                metadatas=metadatas,
                ids=ids
            )
            print(f"Successfully added {len(chunks)} chunks from {filename}.")
        except Exception as e:
            print(f"Error processing {filename}: {e}")

if __name__ == "__main__":
    run_ingestion()
