import sqlite3
import datetime

# Database setup
DB_NAME = "security_logs.db"

def initialize_database():
    """Creates the database and logs table if not exists."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            severity TEXT,
            message TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def log_security_event(severity, message):
    """Logs a security event into the database."""
    if not severity or not message:
        print("⚠️ Improper logging detected: Missing severity or message.")
        return False
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Check for improper logging
    if "error occurred" in message.lower() or severity.upper() not in ["INFO", "WARNING", "ERROR"]:
        print(f"⚠️ Improper logging detected: {message}")
        return False

    # Insert log into the database
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO logs (timestamp, severity, message)
        VALUES (?, ?, ?)
    ''', (timestamp, severity.upper(), message))

    conn.commit()
    conn.close()

    print(f"✅ Log saved: [{severity.upper()}] {message}")
    return True

def check_improper_logs():
    """Checks database for improper logs."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM logs WHERE message LIKE '%error occurred%' OR severity NOT IN ('INFO', 'WARNING', 'ERROR')
    ''')
    
    improper_logs = cursor.fetchall()
    conn.close()

    if improper_logs:
        print("\n⚠️ Improper logs found:")
        for log in improper_logs:
            print(log)
    else:
        print("\n✅ No improper logs found.")

# Main execution
if __name__ == "__main__":
    initialize_database()

    # Example Logs
    log_security_event("INFO", "User login successful")
    log_security_event("WARNING", "Multiple failed login attempts detected")
    log_security_event("ERROR", "Database connection lost")
    log_security_event("", "error occurred")  # Improper log example
    log_security_event("DEBUG", "This is a debug log")  # Improper log example

    # Check for improper logs
    check_improper_logs()
