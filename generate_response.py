from typing import List
from datetime import datetime

class ResponseGenerator:
    def __init__(self, model_name: str = None):
        self.model_name = model_name

    def generate_html(self, query: str, results: List) -> str:
        """Generates a beautiful HTML email body with images, tables, and buttons."""
        top_match = results[0].metadata
        top_text = results[0].text 

        city = top_match.get('city', 'your desired city')
        duration = top_match.get('duration_days', 'Several')
        people = top_match.get('people', 'your group')
        price = top_match.get('price', 'Contact us')
        hotel = top_match.get('hotel', 'Premium Accommodation')

        header_image_url = "https://images.unsplash.com/photo-1436491865332-7a61a109cc05?w=600&q=80"

        html_template = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
            <div style="max-width: 600px; margin: auto; border: 1px solid #ddd; border-radius: 8px; overflow: hidden;">
                <img src="{header_image_url}" alt="Travel Destination" style="width: 100%; height: 200px; object-fit: cover;">
                <div style="padding: 20px;">
                    <h2 style="color: #2c3e50; text-align: center;">Your Travel Package is Ready</h2>
                    <p>Dear Traveler,</p>
                    <p>Thank you for your interest! Based on your request for <strong>{query}</strong>, we have curated the perfect package for you in {city}.</p>
                    <p><strong>Package Highlights:</strong> {top_text}</p>
                    <p>We have attached a formal, detailed quotation letter to this email for your review.</p>
                    <hr style="border: none; border-top: 1px solid #eee; margin-top: 30px;">
                    <p style="font-size: 12px; color: #777; text-align: center;">
                        This is an automated message from Your Travel Support Team.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        return html_template.strip()

    def generate_pdf_html(self, query: str, results: List) -> str:
        """Generates a formal Quotation Letter specifically for the PDF document."""
        top_match = results[0].metadata
        
        city = top_match.get('city', 'your desired city')
        hotel = top_match.get('hotel', 'Premium Accommodation')
        duration = top_match.get('duration_days', 1)
        total_price = float(top_match.get('price', 0))
        
        # Calculate a logical breakdown for the quotation
        base_price = round(total_price * 0.85, 2)
        taxes = round(total_price - base_price, 2)
        
        current_date = datetime.now().strftime("%B %d, %Y")

        pdf_template = f"""
        <html>
        <head>
        <style>
            body {{ font-family: Helvetica, sans-serif; font-size: 11pt; color: #333; }}
            .header-table {{ width: 100%; border-bottom: 2px solid #d4af37; padding-bottom: 10px; margin-bottom: 30px; }}
            .logo-text {{ font-size: 24pt; font-weight: bold; color: #b8860b; }}
            .company-info {{ text-align: right; font-size: 9pt; color: #555; line-height: 1.4; }}
            .title {{ text-align: center; font-size: 18pt; font-weight: bold; margin-bottom: 30px; color: #2c3e50; }}
            .invoice-table {{ width: 100%; border-collapse: collapse; margin-top: 20px; margin-bottom: 20px; }}
            .invoice-table th {{ background-color: #f8f9fa; border: 1px solid #ddd; padding: 10px; text-align: center; font-weight: bold; }}
            .invoice-table td {{ border: 1px solid #ddd; padding: 10px; text-align: center; }}
            .text-left {{ text-align: left !important; }}
            .btn {{ background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; font-weight: bold; border-radius: 4px; }}
        </style>
        </head>
        <body>
            
            <table class="header-table">
                <tr>
                    <td width="50%" valign="top">
                        <span class="logo-text">ASIA HOTEL Co.</span><br>
                        <span style="font-size: 10pt; color: #777;">Premium Travel & Stays</span>
                    </td>
                    <td width="50%" class="company-info" valign="top">
                        123 Paradise Avenue<br>
                        inquire@asiahotel.mail<br>
                        222 555 7777<br>
                        www.asiahotel.com
                    </td>
                </tr>
            </table>

            <div class="title">QUOTATION LETTER</div>

            <p><b>Date:</b> {current_date}</p>
            <p>Dear Client,</p>
            <p>Thank you very much for your interest in our travel services.</p>
            <p>We are delighted to provide you with a detailed estimate for the services you requested for your upcoming {duration}-day trip to <b>{city}</b>. We have more than 30 years of experience in the field of hospitality, and we would like to bring you the most comfortable feeling when traveling and relaxing. Below is an itemized list of the estimated costs for your package, which includes a premium stay at <b>{hotel}</b>.</p>

            <table class="invoice-table" cellpadding="6">
                <tr>
                    <th class="text-left">Service Description</th>
                    <th>Quantity</th>
                    <th>Cost per Unit</th>
                    <th>Total Cost</th>
                </tr>
                <tr>
                    <td class="text-left">{city} Premium Tour Package</td>
                    <td>1</td>
                    <td>${base_price:.2f}</td>
                    <td>${base_price:.2f}</td>
                </tr>
                <tr>
                    <td class="text-left">Accommodation ({hotel})</td>
                    <td>{duration} Nights</td>
                    <td>Included</td>
                    <td>Included</td>
                </tr>
                <tr>
                    <td class="text-left">Taxes & Service Surcharges (15%)</td>
                    <td>1</td>
                    <td>${taxes:.2f}</td>
                    <td>${taxes:.2f}</td>
                </tr>
                <tr>
                    <td colspan="3" style="text-align: right; font-weight: bold; padding-right: 15px;">Grand Total</td>
                    <td style="font-weight: bold;">${total_price:.2f}</td>
                </tr>
            </table>

            <p>We are committed to ensuring your trip is successful and memorable. If you have any special requests or need further customization, please do not hesitate to contact us. We are more than happy to discuss additional services or adjustments to meet your exact needs.</p>
            
            <p>Thank you for considering our company for your travels. We look forward to the opportunity to welcome you!</p>

            <div style="text-align: center; margin-top: 40px;">
                <a href="https://coactivesolutions.co.in/" class="btn">Confirm & Book Now</a>
            </div>

        </body>
        </html>
        """
        return pdf_template.strip()