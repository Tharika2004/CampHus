import mysql.connector
from config import DB_CONFIG

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def is_event_duplicate(event_name, college_name, city, venue, event_date):
    try:
        conn = get_db_connection()
        # 'buffered=True' kandippa irukkanum, illana 'Unread result' error thirumba varum
        cursor = conn.cursor(buffered=True) 
        
        # Inga namma UPPER() use pandroam, unga DB style-ku match aaga
        query = """
            SELECT id FROM events 
            WHERE UPPER(TRIM(event_name)) = UPPER(TRIM(%s)) 
            AND UPPER(TRIM(college_name)) = UPPER(TRIM(%s)) 
            AND UPPER(TRIM(city)) = UPPER(TRIM(%s)) 
            AND UPPER(TRIM(venue)) = UPPER(TRIM(%s))
            AND event_date = %s
        """
        
        cursor.execute(query, (event_name, college_name, city, venue, event_date))
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        return result is not None
    except Exception as e:
        print(f"⚠️ Duplicate Check Error: {e}")
        return False

def get_all_data_json():
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM events ORDER BY id DESC")
        result = cursor.fetchall()
        cursor.close()
        return result
    except Exception as e:
        print(f"Error: {e}")
        return []
    finally:
        if connection and connection.is_connected():
            connection.close()

# FIX: Updated to accept and store 'name' along with 'email'
def add_user_email(email, name=None):
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
       
        # This will insert the user, or update the name if the email already exists
        query = """
            INSERT INTO users (email, name)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE name = %s
        """
        cursor.execute(query, (email, name, name))
       
        connection.commit()
        cursor.close()
        return True
    except Exception as e:
        print(f"Database Error in add_user_email: {e}")
        return False  
    finally:
        if connection and connection.is_connected():
            connection.close()

def get_all_users_json():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        # Fetch both for better visibility
        cursor.execute("SELECT name, email FROM users")
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result
    except Exception as e:
        print(f"Error: {e}")
        return []
    
def get_all_user_emails():
    try:
        conn = get_db_connection()
        cursor = conn.cursor() # Dictionary=True thevai illai, verum list dhaan venum
        cursor.execute("SELECT email FROM users")
        
        # Row-la irundhu email-ai mattum eduthu list-ah mathuroam
        emails = [row[0] for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        return emails # Output: ['abc@gmail.com', 'xyz@gmail.com']
    except Exception as e:
        print(f"Error fetching email list: {e}")
        return []
         
         
         