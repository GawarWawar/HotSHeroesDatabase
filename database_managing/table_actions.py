import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2.errors import DuplicateTable, UniqueViolation
from instance_actions import InstanceActions, RolesInstance, HeroesInstance

def create_class_instances_from_elements (
    elements: list,
    instance_class: InstanceActions,
):
    elements_to_return = []
    for element in elements:
        element = element[1:]+(element[0],)
        element = instance_class(*element)
        elements_to_return.append(element)
    return elements_to_return

class TableActions ():
    def __init_subclass__(
        cls, 
        instance_class: InstanceActions
    ) -> None:
        cls.instance_class = instance_class
    
    def get_table_columns (self):
        with psycopg2.connect(
                database = "postgres", user = "postgres", 
                host= 'localhost', password = "123qwedsacxz",
                port = 5432
            ) as conn:
                with conn.cursor() as cur:
                    cur.execute(f"""SELECT * FROM {self.instance_class.table}
                                LIMIT 1""")
                    column_names = [desc[0] for desc in cur.description]
                return column_names
        
    def select_rows (
        self,
        *args, **kwargs
    ):
        """
    Select rows from the database table specified by `self.instance_class.table` based on the given class parameter.

    Args:
        *args: Positional arguments (strings) for selecting all columns.
               Use "all" as a single positional argument.

        **kwargs: Keyword arguments for specifying filtering criteria.
                  The keys should correspond to column names, and the values
                  are used to filter rows based on those columns.

    Returns:
        List of instances of `self.instance_class` representing the selected rows.

    Raises:
        psycopg2.OperationalError: If there is an issue with the database connection or execution.
    """
        
        if "all" in args:
            sql = f"SELECT * FROM {self.instance_class.table}"
            values = ()
        if kwargs:
            print(kwargs)
            sql_where_string = ""
            values = []
            for cycle_count, column in enumerate(kwargs):
                if cycle_count == 0:
                    string_to_add = f"{column}=%s "
                else:
                    string_to_add = f"AND {column}=%s "
                values.append(kwargs.get(column))
                sql_where_string = sql_where_string+string_to_add
            values = tuple(values)
            sql = f"""SELECT * FROM {self.instance_class.table} 
                    WHERE {sql_where_string}
                    """
        with psycopg2.connect(
            database = "postgres", user = "postgres", 
            host= 'localhost', password = "123qwedsacxz",
            port = 5432
        ) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, values
                )
                elements = cur.fetchall()
            elements_to_return = create_class_instances_from_elements(
                elements,
                self.instance_class
            )
            return elements_to_return
            

                

class RolesTable (TableActions, instance_class = RolesInstance):
    pass

class HeroesTable (TableActions, instance_class = HeroesInstance):
    pass

if __name__ == "__main__":
    roles_table = RolesTable()
    print(roles_table.select_rows("all"))
    heroes_table = HeroesTable()
    print(heroes_table.get_table_columns())
    print(heroes_table.select_rows( id = 15, name = "Jaina"))
    