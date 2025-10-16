import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


class TestProductModel(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        db.session.close()

    def setUp(self):
        db.session.query(Product).delete()
        db.session.commit()

    def tearDown(self):
        db.session.remove()

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    def test_read_a_product(self):
        """It should Read a Product"""
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        found_product = Product.find(product.id)
        self.assertEqual(found_product.id, product.id)
        self.assertEqual(found_product.name, product.name)
        self.assertEqual(found_product.description, product.description)
        self.assertEqual(found_product.price, product.price)

    def test_update_a_product(self):
        """It should Update a Product"""
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        product.description = "testing"
        original_id = product.id
        product.update()
        self.assertEqual(product.id, original_id)
        self.assertEqual(product.description, "testing")
        products = Product.all()
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].id, original_id)
        self.assertEqual(products[0].description, "testing")

    def test_delete_a_product(self):
        """It should Delete a Product"""
        product = ProductFactory()
        product.create()
        self.assertEqual(len(Product.all()), 1)
        product.delete()
        self.assertEqual(len(Product.all()), 0)

    def test_list_all_products(self):
        """It should List all Products in the database"""
        products = Product.all()
        self.assertEqual(products, [])
        for _ in range(5):
            product = ProductFactory()
            product.create()
        products = Product.all()
        self.assertEqual(len(products), 5)

    def test_find_by_name(self):
        """It should Find a Product by Name"""
        products = ProductFactory.create_batch(5)
        for product in products:
            product.create()
        name = products[0].name
        count = len([product for product in products if product.name == name])
        found = Product.find_by_name(name)
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertEqual(product.name, name)

    def test_find_by_availability(self):
        """It should Find Products by Availability"""
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        available = products[0].available
        count = len([product for product in products if product.available == available])
        found = Product.find_by_availability(available)
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertEqual(product.available, available)

    def test_find_by_category(self):
        """It should Find Products by Category"""
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        category = products[0].category
        count = len([product for product in products if product.category == category])
        found = Product.find_by_category(category)
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertEqual(product.category, category)

    def test_find_by_price(self):
        """It should Find Products by Price"""
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        price = products[0].price
        count = len([product for product in products if product.price == price])
        found = Product.find_by_price(price)
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertEqual(product.price, price)

    def test_find_by_price_string(self):
        """It should Find Products by Price as string"""
        products = ProductFactory.create_batch(5)
        for product in products:
            product.create()
        price_str = str(products[0].price)
        found = Product.find_by_price(price_str)
        self.assertIsNotNone(found)

    def test_update_without_id(self):
        """It should not Update a Product without an id"""
        product = ProductFactory()
        product.id = None
        self.assertRaises(Exception, product.update)

    def test_deserialize_a_product(self):
        """It should Deserialize a product"""
        data = {
            "name": "Hat",
            "description": "A nice hat",
            "price": "19.99",
            "available": True,
            "category": "CLOTHS"
        }
        product = Product()
        product.deserialize(data)
        self.assertIsNotNone(product)
        self.assertEqual(product.name, "Hat")
        self.assertEqual(product.description, "A nice hat")
        self.assertEqual(product.price, 19.99)
        self.assertEqual(product.available, True)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_deserialize_with_no_name(self):
        """It should not Deserialize a product without a name"""
        data = {
            "description": "A nice hat",
            "price": "19.99",
            "available": True,
            "category": "CLOTHS"
        }
        product = Product()
        self.assertRaises(Exception, product.deserialize, data)

    def test_deserialize_with_no_data(self):
        """It should not Deserialize a product with empty data"""
        data = {}
        product = Product()
        self.assertRaises(Exception, product.deserialize, data)

    def test_deserialize_with_bad_data(self):
        """It should not Deserialize bad data"""
        data = "this is not a dictionary"
        product = Product()
        self.assertRaises(Exception, product.deserialize, data)

    def test_deserialize_bad_available(self):
        """It should not Deserialize bad available attribute"""
        data = {
            "name": "Hat",
            "description": "A nice hat",
            "price": "19.99",
            "available": "not_boolean",
            "category": "CLOTHS"
        }
        product = Product()
        self.assertRaises(Exception, product.deserialize, data)

    def test_deserialize_bad_category(self):
        """It should not Deserialize bad category"""
        data = {
            "name": "Hat",
            "description": "A nice hat",
            "price": "19.99",
            "available": True,
            "category": "INVALID_CATEGORY"
        }
        product = Product()
        self.assertRaises(Exception, product.deserialize, data)

    def test_serialize_a_product(self):
        """It should Serialize a product"""
        product = ProductFactory()
        data = product.serialize()
        self.assertIsNotNone(data)
        self.assertIn("id", data)
        self.assertEqual(data["name"], product.name)
        self.assertEqual(data["description"], product.description)
        self.assertEqual(Decimal(data["price"]), product.price)
        self.assertEqual(data["available"], product.available)
        self.assertEqual(data["category"], product.category.name)

    def test_product_string_representation(self):
        """It should return string representation of product"""
        product = ProductFactory()
        product.create()
        self.assertEqual(str(product), f"<Product {product.name} id=[{product.id}]>")

    def test_product_repr(self):
        """It should return repr of product"""
        product = ProductFactory()
        product.create()
        self.assertIn(product.name, repr(product))
        self.assertIn(str(product.id), repr(product))
