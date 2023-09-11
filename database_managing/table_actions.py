import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2.errors import DuplicateTable, UniqueViolation
from instance_actions import InstanceActions, RolesInstance, HeroesInstance

def create_class_instances_from_elements (
    elements: list,
    instance_class: InstanceActions
):
    elements_to_return = []
    for element in elements:
        element = element[1:]
        element = instance_class(*element)
        elements_to_return.append(element)
    return elements_to_return

class TableActions ():
    def __init_subclass__(
        cls, 
        table_name:str,
        instance_class: InstanceActions
    ) -> None:
        cls.table_name = table_name
        cls.instance_class = instance_class
        
    def select_all (
        self
    ):
        with psycopg2.connect(
                database = "postgres", user = "postgres", 
                host= 'localhost', password = "123qwedsacxz",
                port = 5432
            ) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        f"""SELECT * FROM {self.table_name} 
                        """
                    )
                    elements = cur.fetchall()
                    print(elements)
                    elements_to_return = create_class_instances_from_elements(
                        elements,
                        self.instance_class
                    )
                    return elements_to_return
    
    def select_rows_by_column_value_combination (
        self, 
        column: str, 
        value: tuple
    ):
        with psycopg2.connect(
                database = "postgres", user = "postgres", 
                host= 'localhost', password = "123qwedsacxz",
                port = 5432
            ) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        f"""SELECT * FROM {self.table_name} 
                        WHERE {column}=%s
                        """, (value)
                    )
                    elements_to_return = create_class_instances_from_elements(
                        cur.fetchall(),
                        self.instance_class
                    )
                    return elements_to_return

class RolesTable (TableActions, table_name = "roles", instance_class = RolesInstance):
    pass

class HeroesTable (TableActions, table_name = "heroes", instance_class = HeroesInstance):
    pass

if __name__ == "__main__":
    roles_table = RolesTable()
    print(
        roles_table.select_rows_by_column_value_combination(
            "id",
            (1,)
        )
    )
    heroes_table = HeroesTable()
    print(heroes_table.select_all())
    print(heroes_table.select_rows_by_column_value_combination(
        "name",
        ("a",)
    ))
    