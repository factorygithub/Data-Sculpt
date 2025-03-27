import sqlite3
import datetime

# 📌 Connect to SQLite Database (or create if it doesn't exist)
conn = sqlite3.connect("security_logs.db")
cursor = conn.cursor()

# 📌 Create a Table for Logging Events
cursor.execute("""
CREATE TABLE IF NOT EXISTS security_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    log_level TEXT,
    message TEXT
)
""")
conn.commit()

# 📌 Function to Insert a Log into the Database
def log_event(log_level, message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO security_logs (timestamp, log_level, message) VALUES (?, ?, ?)", 
                   (timestamp, log_level, message))
    conn.commit()
    print(f"📌 Log Added: [{log_level}] {message}")

# 📌 Generate Sample Logs
log_event("INFO", "System initialized successfully.")
log_event("WARNING", "Multiple failed login attempts detected.")
log_event("ERROR", "Unauthorized access detected on server.")

# 📌 Fetch and Display Logs
cursor.execute("SELECT * FROM security_logs")
logs = cursor.fetchall()

print("\n🔍 Stored Logs in Database:")
for log in logs:
    print(log)

# 📌 Close Database Connection
conn.close()
