import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2.errors import DuplicateTable, UniqueViolation
from instance_actions import InstanceObject, RolesInstance, HeroesInstance

def create_class_instances_from_elements (
    elements: list,
    instance_class: InstanceObject,
):
    elements_to_return = []
    for element in elements:
        #element = element[1:]+(element[0],)
        element = instance_class(*element)
        elements_to_return.append(element)
    return elements_to_return

class TableObject ():
    def __init_subclass__(
        cls, 
        instance_class: InstanceObject
    ) -> None:
        cls.instance_class = instance_class
    
        
    def select_rows (
        self,
        *args, **kwargs
    ):
        """
    Select rows from the database table specified by `self.instance_class.table` based on the given class parameter.

    Args:
        *args: Positional argument (string) for selecting all columns.
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
                cur.execute(sql, values)
                elements = cur.fetchall()
            elements_to_return = create_class_instances_from_elements(
                elements,
                self.instance_class
            )
            return elements_to_return
            
    def add_rows (
        self,
        rows_to_add: list[InstanceObject]
    ):
        columns = self.instance_class.table_columns_info
        rows_count = len(rows_to_add)
        with psycopg2.connect(
                database = "postgres", user = "postgres", 
                host= 'localhost', password = "123qwedsacxz",
                port = 5432
            ) as conn:
                with conn.cursor() as cur:
                    try:
                        if rows_count>1:
                            sql_values = ' '.join(['%s,'] * (rows_count-1))
                            sql_values = sql_values + '%s'
                        else:
                            sql_values  = ' '.join(['%s'])
                        for row in range(rows_count):
                            rows_to_add[row] = rows_to_add[row].to_tuple()
                        
                        print(rows_to_add)
                        column_names = []
                        for column in self.instance_class.table_columns_info:
                            column_names.append (self.instance_class.table_columns_info[column]["name"])
                        sql = f"""
                            INSERT INTO {self.instance_class.table} ({', '.join(column_names)}) 
                            VALUES {sql_values}
                            """
                        sql = sql + "RETURNING *"
                        cur.execute(
                            sql, rows_to_add
                        )
                    except UniqueViolation:
                        
                        # DOESNT WORK -> psycopg2.ProgrammingError: no results to fetch
                        # NEEEDS ANOTHER METHOD TO GET UniqueViolation RESULTS
                        # elements = cur.fetchall()
                        # conn.rollback()
                        # return f"UniqueViolation was raised with {elements}"
                        pass
                    else:     
                        elements = cur.fetchall()
                        conn.commit()
                        return f"Instances are created sucsessfully {elements}"

                

class RolesTable (TableObject, instance_class = RolesInstance):
    pass

class HeroesTable (TableObject, instance_class = HeroesInstance):
    pass

if __name__ == "__main__":
    roles_table = RolesTable()
    heroes_table = HeroesTable()
    print(heroes_table.select_rows( id = 15, name = "Jaina"))
    rows = roles_table.select_rows("all")
    print(rows)
    print(roles_table.add_rows(rows))
    