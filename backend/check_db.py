import sys
import os
import psycopg2

def check_connection():
    db_url = os.environ.get("DATABASE_URL")
    
    try:
        if db_url:
            # Ensure Neon SSL mode is present
            if "sslmode=" not in db_url:
                db_url += ("&" if "?" in db_url else "?") + "sslmode=require"
            print(f"--> Attempting connection via DATABASE_URL...")
            conn = psycopg2.connect(db_url)
        else:
            host = os.environ.get("DB_HOST", "NOT_SET")
            print(f"--> Attempting connection to host: {host}...")
            conn = psycopg2.connect(
                dbname=os.environ.get("DB_NAME"),
                user=os.environ.get("DB_USER"),
                password=os.environ.get("DB_PASSWORD"),
                host=host,
                port=os.environ.get("DB_PORT", "5432"),
                sslmode=os.environ.get("DB_SSLMODE", "require")
            )
        conn.close()
        print("--> Connection successful!")
        sys.exit(0)
    except Exception as e:
        # Print actual error message directly to stderr
        print(f"--> [DB ERROR DETAILS]: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    check_connection()