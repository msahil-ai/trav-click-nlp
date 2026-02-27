from db_connection import get_connection

def get_supported_countries() -> set:
    """Fetches a distinct list of supported countries from Postgres."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Querying the countries table based on the schema
    cursor.execute("SELECT DISTINCT countryname FROM countries;") # Adjusted to match the actual table and column names in pgAdmin
    
    # Lowercase everything and put it in a set for lightning-fast lookups
    countries = {row[0].lower() for row in cursor.fetchall() if row[0]}
    
    cursor.close()
    conn.close()
    return countries

def check_all_fallbacks(email: dict, supported_countries: set) -> bool:
    """
    Evaluates the email against all fallback rules.
    Returns True if a fallback was triggered (skip the email).
    Returns False if the email is valid and should be processed.
    """
    # Fallback 1: Check if the email JSON is completely empty {}
    if not email: 
        print("Unable to process your email. Kindly re-send a new email")
        return True

    # Fallback 2: Check if the requested country is in our database
    requested_country = email.get("country_to_travel")
    if requested_country and requested_country.lower() not in supported_countries:
        print("We are not able to process your requested country")
        return True

    # If it passes all checks, return False (no fallbacks triggered)
    return False