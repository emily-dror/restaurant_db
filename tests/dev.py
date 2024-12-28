import os
import sys
import unittest
from tabulate import tabulate

SRC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src")
sys.path.append(os.path.abspath(SRC_DIR))

from Solution import *
from Utility.ReturnValue import ReturnValue
from Business.Customer import Customer, BadCustomer

def get_customers():
    conn = None
    rows_effected, result = 0, ResultSet()
    try:
        conn = Connector.DBConnector()
        rows_effected, result = conn.execute("SELECT * FROM Customers")
        # rows_effected is the number of rows received by the SELECT
    except DatabaseException.ConnectionInvalid as e:
        print(e)
    except DatabaseException.NOT_NULL_VIOLATION as e:
        print(e)
    except DatabaseException.CHECK_VIOLATION as e:
        print(e)
    except DatabaseException.UNIQUE_VIOLATION as e:
        print(e)
    except DatabaseException.FOREIGN_KEY_VIOLATION as e:
        print(e)
    except Exception as e:
        print(e)
    finally:
        conn.close()
        return result


def print_table(tbl):
    if tbl.isEmpty():
        print("Empty Table")
        return

    print(
        tabulate(
            [[val for val in row.values()] for row in tbl],
            headers=[str(col) for col in tbl[0]],
            tablefmt="grid",
        )
    )

if __name__ == "__main__":
    # Create Empty Tables
    create_tables()

    # Add Customers
    add_customer(Customer(1, "leah", 22, "0535245288"))
    add_customer(Customer(2, "emily", 22, "0504868405"))
    add_customer(Customer(2, "emily", 22, "0504868407"))

    # Print Table
    print_table(get_customers())

    # Get Customers (good and bad)
    print(get_customer(1))
    print(get_customer(3))

    # Delete Customer
    print(delete_customer(5))

    # Print Table
    print_table(get_customers())

    # Clear Tables
    clear_tables()

    # Print Table
    print_table(get_customers())

    # Drop All Tables
    drop_tables()

