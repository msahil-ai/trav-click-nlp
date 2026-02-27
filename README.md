# 📧 NLP–OCR Email Processing & RAG Automation System

**Automated Travel & Hotel Booking Information Extraction and Recommendation**

---

## 📌 Overview

This project is an **end-to-end automated AI travel agent**. It consists of two powerful phases:

1. **The Ingestion Phase:** Reads real emails from Gmail, extracts meaningful booking-related information using an **LLM-powered NLP pipeline**, and stores the results in structured JSON format.
2. **The Recommendation Phase (RAG):** Analyzes the extracted JSON, searches a customized PostgreSQL and Vector database for the perfect travel package, generates a dynamic HTML email and PDF quotation, and automatically replies to the customer.

It is designed to handle high email volume (1500+ emails/hour), process mixed formats incrementally, and provide personalized, instantly bookable itineraries.

---

## 🏗️ High-Level Architecture

The system flows from a customer's raw email straight to a formatted PDF quotation response.

### Phase 1: Ingestion & Extraction (NLP)

```text
Gmail Inbox
   ↓
Email Fetcher (IMAP + UID-based tracking)
   ↓
Keyword Filtering (Hotel / Travel Queries)
   ↓
Text Cleaning & Normalization
   ↓
Gemma LLM (Information Extraction)
   ↓
Saved Output (One JSON per email)

```

### Phase 2: Retrieval & Response (RAG)

```text
Extracted JSON (Customer Request)
   ↓
Fallback Validation (Check if country/data is supported)
   ↓
ChromaDB Vector Search (Semantic "Vibe" Match)
   ↓
Rule-Based Filtering (Exact city, min duration, min capacity)
   ↓
Dynamic Template Generation (HTML Email + Formal Quotation)
   ↓
PDF Conversion (xhtml2pdf)
   ↓
SMTP Dispatch (Automated Reply to Customer)

```

---

## 🧠 Part 1: Email Processing & Extraction

### Primary Model

* **Gemma 2B Instruction-Tuned**
* Fine-tuned for structured information extraction.
* Optimized for speed, cost efficiency, and deterministic JSON output.

### Email Processing Strategy

* **Inbox Scope:** Only Primary Inbox is processed.
* **Incremental Processing:** Uses **Gmail UID-based tracking** to guarantee no duplicates or missed emails.
* **Filtering Logic:** Only processes emails containing booking-related keywords (e.g., *hotel, booking, trip, vacation*).

### Output Format (The Handoff)

Each processed email generates a separate JSON file, which triggers Phase 2:

```json
{
  "full_name": "Sahil Khan",
  "email": "sahilkhan@email.com",
  "tour_start_date": "12 June 2026",
  "city_to_travel": "Singapore",
  "number_of_adults": "5",
  "number_of_children": "2",
  "attractions_to_visit": "Universal Studios"
}

```

---

## ⚙️ Part 2: The RAG Recommendation Pipeline

Once the JSON is extracted, the automated travel agent takes over.

### 🔹 1. Data Embeddings (`embed_DB.py`)

The system bridges structured database data with AI search capabilities. It connects to a PostgreSQL database to retrieve package IDs, city names, prices, and default premium hotels. It handles missing prices gracefully by using SQL `COALESCE` to default null prices to 0. The data is then embedded using `sentence-transformers/all-MiniLM-L6-v2` and permanently stored in a ChromaDB `PersistentClient`.

### 🔹 2. The Bouncer (`fallbacks.py`)

Before wasting compute resources on impossible requests, the system validates the incoming JSON. It fetches a distinct list of supported countries directly from the Postgres database and skips the email if the requested country is unsupported or the JSON is empty.

### 🔹 3. "Exact Match or Better Deal" (`soft_match.py`)

Finding the perfect package requires two steps:

1. **Semantic Search:** ChromaDB finds packages with the right "vibe" based on the user's query.
2. **Rule-Based Reranking:** A strict mathematical filter drops any package that doesn't exactly match the requested city, or fails to meet the minimum required duration or passenger capacity.

### 🔹 4. Dual Generation (`generate_response.py` & `save_pdf_html.py`)

The system generates two beautifully formatted HTML assets:

* **The Email Body:** An interactive HTML email featuring an Unsplash header image, the package highlights, and a styled layout.
* **The Quotation Letter:** A formal, date-stamped HTML invoice featuring a calculated breakdown of base prices and taxes. This specific HTML is then passed to `xhtml2pdf` to instantly generate a physical PDF document.

### 🔹 5. The Mailman (`mailman.py`)

Finally, the system securely connects to Google's SMTP servers. It initiates a fresh `EmailMessage` envelope for every customer, attaches the generated PDF quotation, sets the HTML body, and dispatches the customized itinerary directly to the customer's inbox.

---

## 📁 Project Structure

```text
project/
│
├── main.py                   # Master script to run the entire pipeline end-to-end
├── email_fetcher.py          # Gmail email fetching & UID tracking
├── fetcher_inference.py      # Batch email processing loop (Phase 1)
├── gemma_merged_model.pt     # Fine-tuned Gemma weights
│
├── db_connection.py          # PostgreSQL connection setup
├── embed_DB.py               # Vectorizing DB packages into ChromaDB
├── fallbacks.py              # Validation logic against unsupported requests
├── soft_match.py             # Semantic + Rule-based package filtering
├── generate_response.py          # HTML Email & Invoice template generation
├── save_pdf_html.py          # HTML to PDF conversion logic
├── mailman.py                # SMTP dispatch and attachment handling
├── rag_pipeline.py           # Main orchestration loop for Phase 2
│
├── outputs/                  # Extracted JSON outputs (Handoff point)
├── pdf_responses/            # Generated PDF Quotations
├── tour_vector_db/           # Persistent ChromaDB storage
├── .env                      # Email & Database credentials
└── README.md

```

---

## 🔐 Security Considerations

* Email and Database credentials stored in `.env`.
* Uses Gmail **App Passwords** (No plaintext passwords in code).
* Read-only mailbox access (no email deletion via IMAP).
* `EmailMessage` objects are strictly scoped inside functions to prevent cross-contamination of customer data.

---

## 🚀 How to Run

### 1️⃣ Setup Environment

```bash
pip install -r requirements.txt

```

*(Note: Windows users do not need external dependencies for PDF generation, as `xhtml2pdf` is pure Python).*

### 2️⃣ Configure `.env`

Create a `.env` file in the root directory with the following structure:

```env
# IMAP Extraction & SMTP Dispatch Credentials
EMAIL_HOST=imap.gmail.com
EMAIL_USER=your_email@gmail.com
EMAIL_APP_PASSWORD=your_app_password

# Postgres Database Credentials
DB_HOST=localhost
DB_PORT=5432
DB_NAME=my_database
DB_USER=postgres
DB_PASS=your_db_password

```

### 🚀 Option A: Run the Entire System

Directly run the master orchestration script to fetch emails, extract data, and send responses in one go:

```bash
python main.py

```

### 🚀 Option B: Step-by-Step (For Testing & Debugging)

**3️⃣ Initialize the Vector Database (Run Once)**
Before processing requests, embed your PostgreSQL data into ChromaDB:

```bash
python embed_DB.py

```

**4️⃣ Run the Complete Pipeline in Stages**
*Step A:* Fetch emails and extract JSON via Gemma 2B:

```bash
python fetcher_inference.py

```

*Step B:* Process JSONs, match packages, and send automated PDF replies:

```bash
python rag_pipeline.py

```

---

## ✅ Conclusion

This system bridges the gap between raw, unstructured customer communication and fully automated sales. By combining IMAP integration, localized LLM extraction, vector search, and dynamic document generation, it serves as a **production-ready, cost-efficient, and scalable** AI Travel Agent.
