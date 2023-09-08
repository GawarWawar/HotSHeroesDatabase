import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2.errors import DuplicateTable, UniqueViolation

class InstanceActions ():
    def get_id_by_name(
        self,
        table,
        id = None,
        ) -> None:
        if id == None:
            with psycopg2.connect(
                database = "postgres", user = "postgres", 
                host= 'localhost', password = "123qwedsacxz",
                port = 5432
            ) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        f"""SELECT * FROM {table} 
                        WHERE name=%s
                        """, (self.name,)
                    )
                    element = cur.fetchone()
                    if len(element) == 0:
                        self.id = None
                    else:
                        print(element, element[0])
                        self.id = element[0]
        



class Role ():
    def __init__(
        self, 
        name,
        id = None
    ) -> None:
        self.name = name
        self.table = "roles"
        if id == None:
            with psycopg2.connect(
                database = "postgres", user = "postgres", 
                host= 'localhost', password = "123qwedsacxz",
                port = 5432
            ) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """SELECT * FROM roles 
                        WHERE name=%s
                        """, (self.name,)
                    )
                    element = cur.fetchone()
                    if len(element) == 0:
                        self.id = None
                    else:
                        print(element, element[0])
                        self.id = element[0]
    
    def add_role_to_db (self):
        if self.id == None:
            with psycopg2.connect(
                database = "postgres", user = "postgres", 
                host= 'localhost', password = "123qwedsacxz",
                port = 5432
            ) as conn:
                with conn.cursor() as cur:
                    try:
                        cur.execute(
                            f"""INSERT INTO roles ("name")
                            VALUES (%s)
                            RETURNING *
                            """, (self.name,)
                        )
                    except UniqueViolation:
                        conn.rollback()
                    else:     
                        element = cur.fetchone()
                        conn.commit()
                        self.id = element[0]
                        return f"Role created sucsessfully with id {element[0]}"
        else:
            return f"Role already exist with id {self.id}"
    
    def delete_role_from_db (self):
        with psycopg2.connect(
            database = "postgres", user = "postgres", 
            host= 'localhost', password = "123qwedsacxz",
            port = 5432
        ) as conn:
            if self.id != None:
                with conn.cursor() as cur:
                    cur.execute(
                        """DELETE FROM roles CASCADE
                        WHERE name = %s
                        RETURNING *
                        """, (self.name,)
                    )
                    self.id = None
                    element = cur.fetchone()
                    return f"Role with id {element[0]} deleted"
            else:
                return "This role doesnt exist yet"
                    
                    


class Hero ():
    def __init__(
        self,
        name,
        role: Role,
        id = None
    ) -> None:
        self.name = name,
        self.role_id = role.id
        if id == None:
            with psycopg2.connect(
                database = "postgres", user = "postgres", 
                host= 'localhost', password = "123qwedsacxz",
                port = 5432
            ) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """SELECT * FROM heroes 
                        WHERE name=%s
                        """, (self.name,)
                    )
                    element = cur.fetchone()
                    if len(element) == 0:
                        self.id = None
                    else:
                        self.id = element[0]
    
    def add_player_to_db (self):
        pass
        
        
if __name__ == "__main__":
    
    role_to_add = Role("Assasin")
    print(role_to_add.add_role_to_db())
    print(role_to_add.delete_role_from_db())
    print(role_to_add.add_role_to_db())

# cur.execute("""SELECT * FROM roles""")
# colnames = [desc[0] for desc in cur.description]
# print(colnames)