import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2.errors import DuplicateTable, UniqueViolation
from psycopg2.extensions import Column

class InstanceObject ():
    def __init_subclass__(
        cls,
        table,
        *args, **kwargs
    ) -> None:
        cls.table = table 
        dictionary_with_columns_info = {}
        with psycopg2.connect(
            database = "postgres", user = "postgres", 
            host= 'localhost', password = "123qwedsacxz",
            port = 5432
        ) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                        SELECT COLUMN_NAME, DATA_TYPE
                        FROM information_schema.columns
                        WHERE table_name = '{cls.table}' 
                    """
                )
                columns_info = cur.fetchall()
                for column_number, column in enumerate(columns_info):
                    dictionary_with_columns_info.update(
                        {
                            column_number:{
                                "name": column[0],
                                "dtype": column[1]
                            }
                        }
                    )               
        cls.table_columns_info = dictionary_with_columns_info
    
    def __init__(
        self,
        *args, **kwargs
    ) -> None:
        """
            Initialize an instance of the class with provided values.

            This constructor accepts either positional arguments (*args) or keyword arguments (**kwargs) to initialize
            instance attributes based on the class's predefined table columns. If both args and kwargs are provided, it raises
            an AttributeError. If args are used, they should match the order of columns in the table_columns_info attribute.
            If kwargs are used, they should match the column names.

            Args:
                *args: Positional arguments to initialize instance attributes (should match the order of table columns).
                **kwargs: Keyword arguments to initialize instance attributes (should match column names).

            Raises:
                AttributeError: If both args and kwargs are provided.
        """
        # Initialize an empty list to store attribute values
        value_list = [] 
        
        # Check if both args and kwargs are provided, and raise an error if so
        if args and kwargs:
            raise AttributeError("Function can accept args or kwargs. Choose only one method to use")
        
        # Initialize the value_list based on the provided args or kwargs
        if args:
            value_list = args        
        elif kwargs:
            for column_name in kwargs:
                add_count = 0
                for column in self.table_columns_info:
                    if column_name == self.table_columns_info[column]["name"]:
                        value_list.append(kwargs.get(column_name))
                        add_count += 1
                if add_count == 0:
                    value_list.append(None)
        else:
            # If neither args nor kwargs are provided, initialize with None values
            for column_position in range(len(self.table_columns_info)):
                value_list.append(None)
        
        # Create instance attributes based on column names
        for column_position, column in enumerate(self.table_columns_info):
            column_name = self.table_columns_info[column]["name"]
            setattr(self, column_name, value_list[column_position])     
    
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
    
    def to_dict (
        self,
    ):
        return self.__dict__
    
    def to_list (
        self
    ):
        list_to_return = []
        for key, item in self.__dict__.items():
            list_to_return.append(item)
        return list_to_return
    
    def to_tuple (
        self
    ):
        list_to_return = []
        for key, item in self.__dict__.items():
            list_to_return.append(item)
        return tuple(list_to_return)
    
    # def __str__(self) -> str:
    #     return self.__dict__

class RolesInstance (InstanceObject, table = "roles"):
    pass
                 
class HeroesInstance (InstanceObject, table = "heroes"):
   pass
    
        
if __name__ == "__main__":
    asasin = RolesInstance(1, "Assasin")
    print(asasin.table_columns_info)
    print(HeroesInstance(15, "jaina", 1).to_list())

