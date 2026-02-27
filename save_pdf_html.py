import os
from xhtml2pdf import pisa

def save_response_as_pdf(html_content: str, email_index: int) -> str:
    """
    Takes the generated HTML response and converts it directly into a styled PDF.
    """
    # 1. Define and create the output folder
    output_folder = "pdf_responses"
    os.makedirs(output_folder, exist_ok=True)

    # 2. Set the file path
    filename = f"email_{email_index}_recommendation.pdf"
    file_path = os.path.join(output_folder, filename)

    # 3. Convert HTML to PDF
    # We open the file in "w+b" (write binary) mode, which is required for PDFs
    with open(file_path, "w+b") as result_file:
        pisa_status = pisa.CreatePDF(
            src=html_content,       
            dest=result_file        
        )

    # 4. Check for errors
    if pisa_status.err:
        print(f":: Error creating PDF for email {email_index}")
    else:
        print(f":: Dynamic HTML-to-PDF successfully saved to: {file_path}")

    return file_path