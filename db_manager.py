import psycopg2
from psycopg2 import Error
import os
def connect_to_db():
    try:
        # Database connection parameters
        connection = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT", "5432")
        )
        return connection
    except (Exception, Error) as error:
        print("Error connecting to PostgreSQL:", error)
        return None

def create_table(connection):
    try:
        cursor = connection.cursor()
        
        # Create table query
        create_table_query = """
        CREATE TABLE IF NOT EXISTS user_info (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            email VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        cursor.execute(create_table_query)
        connection.commit()
        print("Table created successfully")
        
    except (Exception, Error) as error:
        print("Error creating table:", error)

def insert_data(connection, name, email):
    try:
        cursor = connection.cursor()
        
        # Insert data query
        insert_query = """
        INSERT INTO user_info (name, email) 
        VALUES (%s, %s) RETURNING id
        """
        cursor.execute(insert_query, (name, email))
        user_id = cursor.fetchone()[0]
        connection.commit()
        print(f"Data inserted successfully. User ID: {user_id}")
        return user_id
        
    except (Exception, Error) as error:
        print("Error inserting data:", error)
        return None

def update_data(connection, user_id, name, email):
    try:
        cursor = connection.cursor()
        
        # Update data query
        update_query = """
        UPDATE user_info 
        SET name = %s, email = %s 
        WHERE id = %s
        """
        cursor.execute(update_query, (name, email, user_id))
        connection.commit()
        print("Data updated successfully")
        
    except (Exception, Error) as error:
        print("Error updating data:", error)

def main():
    # Connect to database
    connection = connect_to_db()
    if connection:
        # Create table
        create_table(connection)
        
        # Insert new user
        user_id = insert_data(connection, "John Doe", "john@example.com")
        
        # Update user
        if user_id:
            update_data(connection, user_id, "John Smith", "john.smith@example.com")
        
        # Close connection
        connection.close()
        print("PostgreSQL connection closed")

if __name__ == "__main__":
    main()
