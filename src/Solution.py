from typing import List, Tuple
from psycopg2 import sql
from datetime import date, datetime
import Utility.DBConnector as Connector
from Utility.DBConnector import ResultSet
from Utility.ReturnValue import ReturnValue
from Utility.Exceptions import DatabaseException
from Business.Customer import Customer, BadCustomer
from Business.Order import Order, BadOrder
from Business.Dish import Dish, BadDish
from Business.OrderDish import OrderDish


# ---------------------------------- CRUD API: ----------------------------------
# Basic database functions


def create_tables() -> None:
    conn = None
    try:
        conn = Connector.DBConnector()
        # TODO - I'm pretty sure is_active in Dishes should not be UNIQUE - Tomer
        create_query = """
            CREATE TABLE Customers (
                cust_id    INTEGER   PRIMARY KEY CHECK (cust_id > 0),
                full_name  TEXT      NOT NULL,
                age        INTEGER   NOT NULL CHECK (age >= 18 AND age <= 120),
                phone      TEXT      NOT NULL CHECK (LENGTH(phone) = 10)
            );

            CREATE TABLE Orders (
                order_id         INTEGER    PRIMARY KEY CHECK (order_id > 0),
                date             TIMESTAMP  NOT NULL,
                delivery_fee     DECIMAL    NOT NULL CHECK (delivery_fee >= 0),
                delivery_address TEXT       NOT NULL CHECK (LENGTH(delivery_address) >= 5)
            );

            CREATE TABLE Dishes (
                dish_id    INTEGER  PRIMARY KEY CHECK (dish_id > 0),
                name       TEXT     NOT NULL CHECK (LENGTH(name) >= 4),
                price      DECIMAL  NOT NULL CHECK (price > 0),
                is_active  BOOLEAN  NOT NULL UNIQUE
            );
            
            CREATE VIEW ActiveDishes AS
                SELECT dish_id, price FROM Dishes WHERE is_active = 1;
            
            CREATE TABLE OrderedBy (
                order_id        INTEGER    PRIMARY KEY REFERENCES Orders(order_id),
                cust_id         INTEGER    REFERENCES Customers(cust_id) ON DELETE CASCADE
            );
            
            CREATE TABLE OrderContains (
                order_id    INTEGER     REFERENCES Orders(order_id),
                dish_id     INTEGER     REFERENCES ActiveDishes(dish_id),
                amount      INTEGER     NOT NULL CHECK (amount>=0),
                price       DECIMAL     NOT NULL,
                UNIQUE (order_id, dish_id)
            );
            
            CREATE TABLE Ratings (
                cust_id    INTEGER   REFERENCES Customers(cust_id) ON DELETE CASCADE,
                dish_id    INTEGER   REFERENCES Dishes(dish_id),
                rating     INTEGER   CHECK (rating >= 1 AND rating <= 5)
                UNIQUE (cust_id, dish_id)
            );
        """
        conn.execute(create_query)
    except DatabaseException.ConnectionInvalid as e:
        # do stuff
        print(e)
    except DatabaseException.NOT_NULL_VIOLATION as e:
        # do stuff
        print(e)
    except DatabaseException.CHECK_VIOLATION as e:
        # do stuff
        print(e)
    except DatabaseException.UNIQUE_VIOLATION as e:
        # do stuff
        print(e)
    except DatabaseException.FOREIGN_KEY_VIOLATION as e:
        # do stuff
        print(e)
    except Exception as e:
        print(e)
    finally:
        # will happen any way after code try termination or exception handling
        conn.close()


def clear_tables() -> None:
    conn = None
    try:
        conn = Connector.DBConnector()
        drop_query = """
            DELETE FROM Customers;
            DELETE FROM Orders;
            DELETE FROM Dishes;
            DELETE FROM OrderedBy;
            DELETE FROM OrderContains;
            DELETE FROM Ratings;
        """
        conn.execute(drop_query)
    except DatabaseException.ConnectionInvalid as e:
        # do stuff
        print(e)
    except DatabaseException.NOT_NULL_VIOLATION as e:
        # do stuff
        print(e)
    except DatabaseException.CHECK_VIOLATION as e:
        # do stuff
        print(e)
    except DatabaseException.UNIQUE_VIOLATION as e:
        # do stuff
        print(e)
    except DatabaseException.FOREIGN_KEY_VIOLATION as e:
        # do stuff
        print(e)
    except Exception as e:
        print(e)
    finally:
        # will happen any way after code try termination or exception handling
        conn.close()


def drop_tables() -> None:
    conn = None
    try:
        conn = Connector.DBConnector()
        # TODO - In piazza the staff said it isn't necessary to use IF EXISTS.
        # TODO - Also, why CASCADE here?
        drop_query = """
            DROP VIEW ActiveDishes;
            DROP TABLE OrderedBy;
            DROP TABLE OrderContains;
            DROP TABLE Ratings;
            DROP TABLE IF EXISTS Customers CASCADE;
            DROP TABLE IF EXISTS Orders CASCADE;
            DROP TABLE IF EXISTS Dishes CASCADE;
        """
        conn.execute(drop_query)
    except DatabaseException.ConnectionInvalid as e:
        # do stuff
        print(e)
    except DatabaseException.NOT_NULL_VIOLATION as e:
        # do stuff
        print(e)
    except DatabaseException.CHECK_VIOLATION as e:
        # do stuff
        print(e)
    except DatabaseException.UNIQUE_VIOLATION as e:
        # do stuff
        print(e)
    except DatabaseException.FOREIGN_KEY_VIOLATION as e:
        # do stuff
        print(e)
    except Exception as e:
        print(e)
    finally:
        # will happen any way after code try termination or exception handling
        conn.close()


# CRUD API
def add_customer(customer: Customer) -> ReturnValue:
    conn = None
    retval = ReturnValue.OK
    try:
        conn = Connector.DBConnector()
        query = sql.SQL(
            "INSERT INTO Customers VALUES({id}, {username}, {age}, {phone})"
        ).format(
            id=sql.Literal(customer.get_cust_id()),
            username=sql.Literal(customer.get_full_name()),
            age=sql.Literal(customer.get_age()),
            phone=sql.Literal(customer.get_phone()),
        )
        rows_effected, _ = conn.execute(query)
    except DatabaseException.NOT_NULL_VIOLATION:
        retval = ReturnValue.BAD_PARAMS
    except DatabaseException.CHECK_VIOLATION:
        retval = ReturnValue.BAD_PARAMS
    except DatabaseException.UNIQUE_VIOLATION:
        retval = ReturnValue.ALREADY_EXISTS
    except Exception as e:
        retval = ReturnValue.ERROR
    finally:
        conn.close()
        return retval


def get_customer(customer_id: int) -> Customer:
    conn = None
    result = ResultSet()
    try:
        conn = Connector.DBConnector()
        query = sql.SQL("SELECT * FROM Customers WHERE cust_id = {id}").format(
            id=sql.Literal(customer_id)
        )
        _, result = conn.execute(query)
    except Exception as e:
        print(e)
    finally:
        conn.close()
        if result.isEmpty():
            return BadCustomer
        return Customer(
            result[0]["cust_id"],
            result[0]["full_name"],
            result[0]["age"],
            result[0]["phone"],
        )


def delete_customer(customer_id: int) -> ReturnValue:
    conn = None
    rows_effected = 0
    try:
        conn = Connector.DBConnector()
        query = sql.SQL(
            "DELETE FROM Customers WHERE cust_id = {id}"
        ).format(id=sql.Literal(customer_id))
        rows_effected, _ = conn.execute(query)
    except Exception as e:
        retval = ReturnValue.ERROR
    finally:
        conn.close()
        if rows_effected == 0:
            return ReturnValue.NOT_EXISTS
        return ReturnValue.OK


def add_order(order: Order) -> ReturnValue:
    conn = None
    retval = ReturnValue.OK
    try:
        conn = Connector.DBConnector()
        query = sql.SQL(
            "INSERT INTO Orders VALUES({id}, {date}, {delivery_fee}, {delivery_address})"
        ).format(
            id=sql.Literal(order.get_order_id()),
            date=sql.Literal(order.get_datetime()),
            delivery_fee=sql.Literal(order.get_delivery_fee()),
            delivery_address=sql.Literal(order.get_delivery_address()),
        )
        rows_effected, _ = conn.execute(query)
    except DatabaseException.NOT_NULL_VIOLATION:
        retval = ReturnValue.BAD_PARAMS
    except DatabaseException.CHECK_VIOLATION:
        retval = ReturnValue.BAD_PARAMS
    except DatabaseException.UNIQUE_VIOLATION:
        retval = ReturnValue.ALREADY_EXISTS
    except Exception as e:
        retval = ReturnValue.ERROR
    finally:
        conn.close()
        return retval


def get_order(order_id: int) -> Order:
    conn = None
    result = ResultSet()
    try:
        conn = Connector.DBConnector()
        query = sql.SQL("SELECT * FROM Orders WHERE order_id = {id}").format(
            id=sql.Literal(order_id)
        )
        _, result = conn.execute(query)
    except Exception as e:
        print(e)
    finally:
        conn.close()
        if result.isEmpty():
            return BadOrder()
        return Order(
            result[0]["order_id"],
            result[0]["date"],
            result[0]["delivery_fee"],
            result[0]["delivery_address"],
        )


def delete_order(order_id: int) -> ReturnValue:
    conn = None
    rows_effected = 0
    try:
        conn = Connector.DBConnector()
        query = sql.SQL(
            "DELETE FROM Orders WHERE order_id = {id}"
        ).format(id=sql.Literal(order_id))
        rows_effected, _ = conn.execute(query)
    except Exception as e:
        return ReturnValue.ERROR
    finally:
        conn.close()
        if rows_effected == 0:
            return ReturnValue.NOT_EXISTS
        return ReturnValue.OK


def add_dish(dish: Dish) -> ReturnValue:
    conn = None
    retval = ReturnValue.OK
    try:
        conn = Connector.DBConnector()
        query = sql.SQL(
            "INSERT INTO Dishes VALUES({id}, {name}, {price}, {is_active})"
        ).format(
            id=sql.Literal(dish.get_dish_id()),
            name=sql.Literal(dish.get_name()),
            price=sql.Literal(dish.get_price()),
            is_active=sql.Literal(dish.get_is_active()),
        )
        rows_effected, _ = conn.execute(query)
    except DatabaseException.NOT_NULL_VIOLATION:
        retval = ReturnValue.BAD_PARAMS
    except DatabaseException.CHECK_VIOLATION:
        retval = ReturnValue.BAD_PARAMS
    except DatabaseException.UNIQUE_VIOLATION:
        retval = ReturnValue.ALREADY_EXISTS
    except Exception as e:
        retval = ReturnValue.ERROR
    finally:
        conn.close()
        return retval


def get_dish(dish_id: int) -> Dish:
    conn = None
    result = ResultSet()
    try:
        conn = Connector.DBConnector()
        query = sql.SQL("SELECT * FROM Dishes WHERE dish_id = {id}").format(
            id=sql.Literal(dish_id)
        )
        _, result = conn.execute(query)
    except Exception as e:
        print(e)
    finally:
        conn.close()
        if result.isEmpty():
            return BadDish()
        return Dish(
            result[0]["dish_id"],
            result[0]["name"],
            result[0]["price"],
            result[0]["is_active"],
        )


def update_dish_price(dish_id: int, price: float) -> ReturnValue:
    conn = None
    rows_effected = 0
    try:
        conn = Connector.DBConnector()
        query = sql.SQL(
            "UPDATE Dishes Set price = {new_price} WHERE dish_id = {id}"
        ).format(
            id=sql.Literal(dish_id),
            new_price=sql.Literal(price),
        )
        rows_effected, _ = conn.execute(query)
    except Exception as e:
        # TODO: BAD_PARAMS if the price is illegal
        return ReturnValue.ERROR
    finally:
        conn.close()
        if rows_effected == 0:
            return ReturnValue.NOT_EXISTS
        return ReturnValue.OK


def update_dish_active_status(dish_id: int, is_active: bool) -> ReturnValue:
    conn = None
    rows_effected = 0
    try:
        conn = Connector.DBConnector()
        query = sql.SQL(
            "UPDATE Dishes Set is_active = {new_active} WHERE dish_id = {id}"
        ).format(
            id=sql.Literal(dish_id),
            new_active=sql.Literal(is_active),
        )
        rows_effected, _ = conn.execute(query)
    except Exception as e:
        # TODO: BAD_PARAMS if the price is illegal
        return ReturnValue.ERROR
    finally:
        conn.close()
        if rows_effected == 0:
            return ReturnValue.NOT_EXISTS
        return ReturnValue.OK


def customer_placed_order(customer_id: int, order_id: int) -> ReturnValue:
    conn = None
    rows_effected = 0
    try:
        conn = Connector.DBConnector()
        query = sql.SQL(
            "INSERT INTO OrderedBy VALUES({order_id}, {customer_id})"
        ).format(
            order_id=sql.Literal(order_id),
            customer_id=sql.Literal(customer_id),
        )
        rows_effected, _ = conn.execute(query)
    except DatabaseException.UNIQUE_VIOLATION:
        return ReturnValue.ALREADY_EXISTS
    except DatabaseException.FOREIGN_KEY_VIOLATION:
        return ReturnValue.NOT_EXISTS

    except Exception as e:
        return ReturnValue.ERROR
    finally:
        conn.close()
    return ReturnValue.OK


def get_customer_that_placed_order(order_id: int) -> Customer:
    conn = None
    result = ResultSet()
    try:
        conn = Connector.DBConnector()
        query = sql.SQL(
            """SELECT * FROM Customers WHERE cust_id IN 
                (SELECT cust_id FROM OrderedBy WHERE order_id = {id})"""
        ).format(
            id=sql.Literal(order_id)
        )
        _, result = conn.execute(query)
    except Exception as e:
        print(e)
    finally:
        conn.close()
    if result.isEmpty():
        return BadCustomer()
    return Customer(
        result[0]["cust_id"],
        result[0]["full_name"],
        result[0]["age"],
        result[0]["phone"]
    )


def order_contains_dish(order_id: int, dish_id: int, amount: int) -> ReturnValue:
    conn = None
    try:
        conn = Connector.DBConnector()
        query = sql.SQL(
            """INSERT INTO OrderContains VALUES({order_id}, {dish_id}, {amount},
                   {(SELECT price FROM ActiveDishes WHERE dish_id = {dish_id})})"""
        ).format(
            order_id=sql.Literal(order_id),
            dish_id=sql.Literal(dish_id),
            amount=sql.Literal(amount)
        )
        rows_effected, _ = conn.execute(query)
    except DatabaseException.UNIQUE_VIOLATION:
        return ReturnValue.ALREADY_EXISTS
    except DatabaseException.FOREIGN_KEY_VIOLATION:
        return ReturnValue.NOT_EXISTS
    except DatabaseException.NOT_NULL_VIOLATION:
        return ReturnValue.BAD_PARAMS
    except DatabaseException.CHECK_VIOLATION:
        return ReturnValue.BAD_PARAMS

    except Exception as e:
        return ReturnValue.ERROR
    finally:
        conn.close()
    return ReturnValue.OK



def order_does_not_contain_dish(order_id: int, dish_id: int) -> ReturnValue:
    conn = None
    rows_effected = 0
    try:
        conn = Connector.DBConnector()
        query = sql.SQL(
            "DELETE FROM OrderContains WHERE order_id = {order_id} AND dish_id = {dish_id}"
        ).format(
            order_id=sql.Literal(order_id),
            dish_id=sql.Literal(dish_id)
        )
        rows_effected, _ = conn.execute(query)
    except Exception as e:
        return ReturnValue.ERROR
    finally:
        conn.close()
        if rows_effected == 0:
            return ReturnValue.NOT_EXISTS
        return ReturnValue.OK


def get_all_order_items(order_id: int) -> List[OrderDish]:
    conn = None
    result = ResultSet()
    try:
        conn = Connector.DBConnector()
        query = sql.SQL(
            "SELECT * FROM OrderContains WHERE order_id = {id} ORDER BY dish_id ASC"
        ).format(
            id=sql.Literal(order_id)
        )
        _, result = conn.execute(query)
    except Exception as e:
        print(e)
    finally:
        conn.close()
    dishList = [OrderDish(item["dish_id"], item["amount"], item["price"]) for item in result]
    return dishList


def customer_rated_dish(cust_id: int, dish_id: int, rating: int) -> ReturnValue:
    conn = None
    try:
        conn = Connector.DBConnector()
        query = sql.SQL(
            "INSERT INTO Ratings VALUES({cust_id}, {dish_id}, {rating})"
        ).format(
            cust_id=sql.Literal(cust_id),
            dish_id=sql.Literal(dish_id),
            rating=sql.Literal(rating)
        )
        rows_effected, _ = conn.execute(query)

    except DatabaseException.UNIQUE_VIOLATION:
        return ReturnValue.ALREADY_EXISTS
    except DatabaseException.FOREIGN_KEY_VIOLATION:
        return ReturnValue.NOT_EXISTS
    except DatabaseException.CHECK_VIOLATION:
        return ReturnValue.BAD_PARAMS
    except Exception as e:
        return ReturnValue.ERROR
    finally:
        conn.close()
    return ReturnValue.OK


def customer_deleted_rating_on_dish(cust_id: int, dish_id: int) -> ReturnValue:
    conn = None
    try:
        conn = Connector.DBConnector()
        query = sql.SQL(
            "DELETE FROM Ratings WHERE cust_id = {cust_id} AND dish_id = {dish_id}"
        ).format(
            cust_id=sql.Literal(cust_id),
            dish_id=sql.Literal(dish_id)
        )
        rows_effected, _ = conn.execute(query)
    except Exception as e:
        return ReturnValue.ERROR
    finally:
        conn.close()

    if rows_effected == 0:
        return ReturnValue.NOT_EXISTS
    return ReturnValue.OK

def get_all_customer_ratings(cust_id: int) -> List[Tuple[int, int]]:
    conn = None
    result = ResultSet()
    try:
        conn = Connector.DBConnector()
        query = sql.SQL(
            "SELECT * FROM Ratings WHERE cust_id = {id} ORDER BY dish_id ASC"
        ).format(
            id=sql.Literal(cust_id)
        )
        _, result = conn.execute(query)
    except Exception as e:
        print(e)
    finally:
        conn.close()
    return [(item["dish_id"], item["rating"]) for item in result]

# ---------------------------------- BASIC API: ----------------------------------

# Basic API


def get_order_total_price(order_id: int) -> float:
    # TODO: implement
    pass


def get_customers_spent_max_avg_amount_money() -> List[int]:
    # TODO: implement
    pass


def get_most_purchased_dish_among_anonymous_order() -> Dish:
    # TODO: implement
    pass


def did_customer_order_top_rated_dishes(cust_id: int) -> bool:
    # TODO: implement
    pass


# ---------------------------------- ADVANCED API: ----------------------------------

# Advanced API


def get_customers_rated_but_not_ordered() -> List[int]:
    # TODO: implement
    pass


def get_non_worth_price_increase() -> List[int]:
    # TODO: implement
    pass


def get_cumulative_profit_per_month(year: int) -> List[Tuple[int, float]]:
    # TODO: implement
    pass


def get_potential_dish_recommendations(cust_id: int) -> List[int]:
    # TODO: implement
    pass
