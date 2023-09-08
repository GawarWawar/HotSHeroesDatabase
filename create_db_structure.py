import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2.errors import DuplicateTable, SyntaxError, UndefinedTable

#    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT) #-> when there is a need to create new dbs

def announce_deletion(
    table_name
):
    print(f"Table {table_name} DELETED")
    
def delete_table_with_cascade(
    table_name,
    conn,
    cur
):
    try:
        cur.execute(
            f"""DROP TABLE {table_name} CASCADE
                """
        )
        announce_deletion("roles")
    except UndefinedTable:
        conn.rollback()
        return False
    else:
        conn.commit()
        return True

def create_db_structure (
    conn ,#:psycopg2.connection,
    cur
):
    cur.execute(
        """CREATE TABLE roles(
            id SERIAL PRIMARY KEY,
            name VARCHAR (100) UNIQUE NOT NULL
        )
        """
    )
    
    cur.execute(
        """CREATE TABLE ability_types(
            id SERIAL PRIMARY KEY,
            name VARCHAR (100) NOT NULL,
            button VARCHAR (20) NOT NULL
        )
        """
    )

    cur.execute(
        """CREATE TABLE heroes(
            id SERIAL PRIMARY KEY, 
            name VARCHAR (100) UNIQUE NOT NULL,
            role_id integer REFERENCES roles (id)
        )
        """
    )
    
    
    cur.execute (
        """ CREATE TABLE abilities(
            id SERIAL PRIMARY KEY,
            name VARCHAR (100) NOT NULL,
            ability_type_id integer REFERENCES ability_types (id),
            hero_id integer REFERENCES heroes (id)
        )
        """
    )
    
    conn.commit()
    
def delete_db_structure (
    conn,
    cur
):
    tables_to_delete =[
        "heroes",
        "roles",
        "abilities",   
        "ability_types",
    ]
    for table in tables_to_delete:
        if delete_table_with_cascade(
            table_name=table,
            conn=conn,
            cur=cur    
        ):
            announce_deletion(table)

if __name__ == "__main__":
    conn = psycopg2.connect(
        database = "postgres", 
        user = "postgres", 
        host= 'localhost',
        password = "123qwedsacxz",
        port = 5432
    )
    
    cur = conn.cursor()
    
    delete_db_structure(
        conn=conn,
        cur=cur
    )
    create_db_structure(
        conn=conn,
        cur=cur
    )
    
    #Close session
    cur.close()
    conn.close()
    print("All done!")