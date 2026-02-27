from ingest import load_all_emails
from soft_match import SoftMatcher
from generate_response import ResponseGenerator
from embed_DB import load_vector_store, load_embed_model
from fallbacks import get_supported_countries, check_all_fallbacks
from save_pdf_html import save_response_as_pdf
from mailman import send_pdf_email


def build_query_from_email(email: dict) -> str:
    parts = []

    if email.get("city_to_travel"):
        parts.append(f"city {email['city_to_travel']}")

    if email.get("country_to_travel"):
        parts.append(f"country {email['country_to_travel']}")

    if email.get("number_of_adults"):
        parts.append(f"{email['number_of_adults']} adults")

    if email.get("number_of_children"):
        parts.append(f"{email['number_of_children']} children")

    return ", ".join(parts)

def chroma_results_to_nodes(results):
    """
    Convert Chroma results → list of objects with .metadata and .text
    """
    nodes = []

    # Safely get both lists from the Chroma results dictionary
    metadatas = results.get("metadatas", [[]])[0]
    documents = results.get("documents", [[]])[0]

    # Zip them together so each node has its matching metadata and text
    for meta, doc in zip(metadatas, documents):
        nodes.append(type("Node", (), {"metadata": meta, "text": doc}))

    return nodes


def main():
    emails = load_all_emails()

    vector_store = load_vector_store()
    embed_model = load_embed_model()

    matcher = SoftMatcher(
        vector_store=vector_store,
        embed_model=embed_model,
        top_k=5
    )

    generator = ResponseGenerator(model_name="mistral")

    # Get the set of supported countries once at the start
    supported_countries = get_supported_countries()

    for idx, email in enumerate(emails, start=1):
        print(f"\n-------------Processing Email {idx}")
        
        # Check all fallbacks before proceeding with matching and generation
        if check_all_fallbacks(email, supported_countries):
            continue

        query = build_query_from_email(email)

        matches = matcher.retrieve(query=query)

        if not matches:
            print("''''''''''No suitable package found")
            continue

        #response = generator.generate(query, matches)
        nodes = chroma_results_to_nodes(matches)

        # 1. Generate both text (for PDF) and HTML (for email)
        # 1. Generate the separate HTML strings!
        email_html = generator.generate_html(query, nodes)
        pdf_html = generator.generate_pdf_html(query, nodes)
        print("\n----------Recommendation generated in HTML format.\n")

        # 2. Save the plain text PDF
        #pdf_path = save_response_as_pdf(response_text=text_response, email_index=idx)
        #pdf_path = save_response_as_pdf(html_content=html_response, email_index=idx) # Save the HTML content as a PDF, which will preserve the styling in the email attachment
        pdf_path = save_response_as_pdf(html_content=pdf_html, email_index=idx)


        # 3. Send the email with the HTML body
        recipient = email.get("email") 
        #send_pdf_email(recipient_email=recipient, pdf_path=pdf_path, html_content=html_response) same body as email text
        send_pdf_email(recipient_email=recipient, pdf_path=pdf_path, html_content=email_html)

    #do not delete the below lines as they are crucial for the flow of the program. They are just commented out for now to prevent errors while testing the new generator.

        #response = generator.generate(query, nodes) # Keep this for backward compatibility if you want to test the old generator
        print("\n........Recommendation:\n")
        #print(response)
        #save_response_as_pdf(response_text=response, email_index=idx)
        #pdf_path = save_response_as_pdf(response_text=response, email_index=idx) #pdf_path 
        recipient = email.get("email") #field in the JSON

        # 3. Send the email!
        #send_pdf_email(recipient_email=recipient, pdf_path=pdf_path)
        send_pdf_email(recipient_email=recipient, pdf_path=pdf_path, html_content=email_html) # Send the email with the HTML body


if __name__ == "__main__":
    main()