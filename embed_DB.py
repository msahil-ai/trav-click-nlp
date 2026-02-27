import psycopg2
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
from db_connection import get_connection
import os

def build_vector_database():
    """Run this function manually when you want to update ChromaDB with new Postgres data."""
    conn = get_connection()
    cursor = conn.cursor()

    # Rewritten to perfectly match the 4 available tables in pgAdmin
    QUERY = """
    SELECT
        p.packageid, 
        c.citname, 
        p.duration_days,
        p.number_of_adults, 
        COALESCE(p.price, 0) AS price, 
        p.attractions,
        STRING_AGG(DISTINCT h.hotname, ', ') AS default_hotel
    FROM packages p
    JOIN cities c ON p.citid = c.citid
    LEFT JOIN hotels h ON h.citid = c.citid AND h.is_default = true
    GROUP BY 
        p.packageid, 
        c.citname, 
        p.duration_days, 
        p.number_of_adults, 
        p.price, 
        p.attractions;
    """

    cursor.execute(QUERY)
    rows = cursor.fetchall()
    print(f".....Loaded {len(rows)} packages from database")

    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    #chroma_client = chromadb.Client(Settings(persist_directory="./tour_vector_db"))
    chroma_client = chromadb.PersistentClient(path="./tour_vector_db")
    
    # We will reset the collection just in case older, broken data is stuck in there
    try:
        chroma_client.delete_collection("tour_packages")
    except ValueError:
        pass # Collection didn't exist yet, which is fine
        
    collection = chroma_client.create_collection(name="tour_packages")

    documents, metadatas, ids = [], [], []

    for row in rows:
        # Unpack the new row structure
        packageid, citname, duration_days, number_of_adults, price, attractions, default_hotel = row
        
        # Fallback just in case a city doesn't have a default hotel assigned yet
        hotel_str = default_hotel if default_hotel else "Standard Premium Accommodation" #hotel requested by client, can be added.

        # Update the embedded text
        text = f"Travel package in {citname}. Duration: {duration_days} days. Suitable for {number_of_adults} adults. Attractions included: {attractions}. Default Hotel: {hotel_str}."
        documents.append(text.strip())
        ids.append(str(packageid))
        
        # Inject the hotel into the metadata!
        metadatas.append({
            "city": citname, 
            "duration_days": int(duration_days), 
            "people": int(number_of_adults), 
            "price": float(price),
            "hotel": hotel_str
        })
        
    embeddings = model.encode(documents, convert_to_numpy=True)
    collection.add(documents=documents, embeddings=embeddings.tolist(), metadatas=metadatas, ids=ids)
    
    print("------Embeddings stored successfully in vector DB")
    cursor.close()
    conn.close()

    # These remain outside so pipeline.py can import them safely!
def load_vector_store():
    #client = chromadb.Client(Settings(persist_directory="./tour_vector_db"))
    client = chromadb.PersistentClient(path="./tour_vector_db")
    return client.get_collection("tour_packages")

def load_embed_model():
    return SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# This is the crucial trigger! It tells Python to actually run the code 
# only when you type 'python embed2.py' in the terminal.
if __name__ == "__main__":
    build_vector_database()