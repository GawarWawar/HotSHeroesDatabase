import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2.errors import DuplicateTable, UniqueViolation

class InstanceActions ():
    def __init_subclass__(
        cls,
        table,
        *args, **kwargs
    ) -> None:
        cls.table = table
    
    def get_id_by_name(
        self,
        id:int = None,
        ) -> int|None:
        if id == None:
            with psycopg2.connect(
                database = "postgres", user = "postgres", 
                host= 'localhost', password = "123qwedsacxz",
                port = 5432
            ) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        f"""SELECT * FROM {self.table} 
                        WHERE name=%s
                        """, (self.name,)
                    )
                    element = cur.fetchone()
                    try:
                        if len(element) == 0:
                            id = None
                        else:
                            id = element[0]
                        return id
                    except TypeError:
                        id = None
                        return id
    
    def add_row_to_table(
        self,
        columns: tuple,
        values: tuple
    ): 
        if self.id == None:
            with psycopg2.connect(
                database = "postgres", user = "postgres", 
                host= 'localhost', password = "123qwedsacxz",
                port = 5432
            ) as conn:
                with conn.cursor() as cur:
                    try:
                        values_representation = []
                        for i in range(len(values)):
                            values_representation.append("%s")
                        
                        cur.execute(
                            f"""INSERT INTO {self.table} ({', '.join(columns)}) 
                            VALUES ({', '.join(['%s'] * len(values))})
                            RETURNING *
                            """, values
                        )
                    except UniqueViolation:
                        conn.rollback()
                        cur.execute(
                            f"""SELECT * FROM {self.table} 
                            WHERE name=%s
                            """, (self.name,)
                        )
                        element = cur.fetchone()
                        return f"UniqueViolation was raised with {element}"
                    else:     
                        element = cur.fetchone()
                        conn.commit()
                        self.id = element[0]
                        return f"Instance in {self.table} created sucsessfully with id {element[0]}"
        else:
            return f"Instance in {self.table} already exist with id {self.id}"
        
    def delete_row_from_table_by_id (
        self, 
        column_with_id_name: str
    ):
        with psycopg2.connect(
            database = "postgres", user = "postgres", 
            host= 'localhost', password = "123qwedsacxz",
            port = 5432
        ) as conn:
            if self.id != None:
                with conn.cursor() as cur:
                    cur.execute(
                        f"""DELETE FROM {self.table} CASCADE
                        WHERE {column_with_id_name}= %s
                        RETURNING *
                        """, (self.id,)
                    )
                    element = cur.fetchone()
                    self.id = None
                    return f"Instance in table {self.table} with id {element[0]} deleted"
            else:
                return f"There no matching instance for this parametrs in table {self.table} yet"


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
                    try:
                        if len(element) == 0:
                            self.id = None
                        else:
                            self.id = element[0]
                    except TypeError:
                        self.id = None
    
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

                    
class Hero (InstanceActions, table = "heroes"):
    def __init__(
        self,
        name,
        role: Role,
        id = None
    ) -> None:
        self.name = name
        self.role_id = role.id
        self.id = self.get_id_by_name(id)
    
    def add_row_to_table(self):
        columns = ("name", "role_id")
        values = (self.name, self.role_id)
        return super().add_row_to_table(columns, values)
    
    def delete_row_from_table_by_id(self):
        column_with_id_name = "id"
        return super().delete_row_from_table_by_id(column_with_id_name)
    
        
        
if __name__ == "__main__":
    
    role = Role("Assasin")
    print(role.add_role_to_db())
    hero = Hero("Jaina", role)
    print(hero.add_row_to_table())
    print(hero.delete_row_from_table_by_id())
    print(hero.add_row_to_table())
    print(hero)

# cur.execute("""SELECT * FROM roles""")
# colnames = [desc[0] for desc in cur.description]
# print(colnames)