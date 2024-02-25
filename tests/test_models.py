"""
Test cases for Pet Model
"""

import os
import logging
from unittest import TestCase
from unittest.mock import patch
from wsgi import app
from service.models import (
    Recommendation,
    RecommendationType,
    DataValidationError,
    db,
)
from tests.factories import RecommendationFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI",
    "postgresql+psycopg://postgres:postgres@localhost:5432/recommendationdb",
)


######################################################################
#  R E C O M M E N D A T I O N   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestCaseBase(TestCase):
    """Test Cases for Recommendation Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Recommendation).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()


######################################################################
#  R E C O M M E N D A T I O N   M O D E L   T E S T   C A S E S
######################################################################
class TestRecommendationModel(TestCaseBase):
    """Recommendation Model CRUD Tests"""

    def test_recommendation_type_values(self):
        """It should contain all desired types of recommendation"""
        target_values = ["UP_SELL", "CROSS_SELL", "ACCESSORY", "BUNDLE"]
        values = [type.value for type in RecommendationType]
        for target_value in target_values:
            self.assertTrue(target_value in values)

    def test_create_recommendation(self):
        """It should Create a recommendation and assert that it exists"""
        recommendation = Recommendation(
            product_a_sku="AA0001",
            product_b_sku="AA0002",
            type=RecommendationType.UP_SELL,
        )
        self.assertEqual(
            str(recommendation), "<Recommendation AA0001-AA0002 id=[None]>"
        )
        self.assertTrue(recommendation is not None)
        self.assertEqual(recommendation.id, None)
        self.assertEqual(recommendation.product_a_sku, "AA0001")
        self.assertEqual(recommendation.product_b_sku, "AA0002")
        self.assertEqual(recommendation.type, RecommendationType.UP_SELL)

        # test new recommendation
        recommendation = Recommendation(
            product_a_sku="AB1111",
            product_b_sku="BA2222",
            type=RecommendationType.CROSS_SELL,
        )
        self.assertEqual(recommendation.product_a_sku, "AB1111")
        self.assertEqual(recommendation.product_b_sku, "BA2222")
        self.assertEqual(recommendation.type, RecommendationType.CROSS_SELL)

    def test_add_recommendation(self):
        """It should create a recommendation and add it to the database"""
        recommendations = Recommendation.all()
        self.assertEqual(recommendations, [])
        recommendation = Recommendation(
            product_a_sku="A1", product_b_sku="B1", type=RecommendationType.UP_SELL
        )
        self.assertTrue(recommendation is not None)
        self.assertEqual(recommendation.id, None)
        recommendation.create()

        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(recommendation.id)
        recommendations = Recommendation.all()
        self.assertEqual(len(recommendations), 1)
        self.assertEqual(recommendations[0].product_a_sku, "A1")
        self.assertEqual(recommendations[0].product_b_sku, "B1")
        self.assertEqual(recommendations[0].type, RecommendationType.UP_SELL)

    def test_read_recommendation(self):
        """It should Read a Recommendation"""
        recommendation = RecommendationFactory()
        logging.debug(recommendation)
        recommendation.id = None
        recommendation.create()
        self.assertIsNotNone(recommendation.id)

        # Fetch it back
        found_recommendation = Recommendation.find(recommendation.id)
        self.assertEqual(found_recommendation.id, recommendation.id)
        self.assertEqual(
            found_recommendation.product_a_sku, recommendation.product_a_sku
        )
        self.assertEqual(
            found_recommendation.product_b_sku, recommendation.product_b_sku
        )
        self.assertEqual(found_recommendation.type, recommendation.type)

    def test_update_recommendation(self):
        """It should Update a Recommendation"""
        recommendation = RecommendationFactory()
        logging.debug(recommendation)
        recommendation.id = None
        recommendation.create()
        logging.debug(recommendation)
        self.assertIsNotNone(recommendation.id)

        # Change it an save it
        recommendation.product_a_sku = "ABC"
        original_id = recommendation.id
        recommendation.update()
        self.assertEqual(recommendation.id, original_id)
        self.assertEqual(recommendation.product_a_sku, "ABC")

        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        recommendations = Recommendation.all()
        self.assertEqual(len(recommendations), 1)
        self.assertEqual(recommendations[0].id, original_id)
        self.assertEqual(recommendations[0].product_a_sku, "ABC")

    def test_update_no_id(self):
        """It should not Update a Recommendation with no id"""
        recommendation = RecommendationFactory()
        logging.debug(recommendation)
        recommendation.id = None
        self.assertRaises(DataValidationError, recommendation.update)

    def test_delete_recommendation(self):
        """It should Delete a Recommendation"""
        recommendation = RecommendationFactory()
        recommendation.create()
        self.assertEqual(len(Recommendation.all()), 1)

        # delete the recommendation and make sure it isn't in the database
        recommendation.delete()
        self.assertEqual(len(Recommendation.all()), 0)

    def test_list_all_recommendations(self):
        """It should List all Recommendations in the database"""
        recommendations = Recommendation.all()
        self.assertEqual(recommendations, [])
        # Create 5 Pets
        for _ in range(5):
            recommendation = RecommendationFactory()
            recommendation.create()
        # See if we get back 5 pets
        recommendations = Recommendation.all()
        self.assertEqual(len(recommendations), 5)

    def test_serialize_recommendation(self):
        """It should serialize a Recommendation"""
        recommendation = RecommendationFactory()
        data = recommendation.serialize()
        self.assertNotEqual(data, None)
        self.assertIn("id", data)
        self.assertEqual(data["id"], recommendation.id)
        self.assertIn("product_a_sku", data)
        self.assertEqual(data["product_a_sku"], recommendation.product_a_sku)
        self.assertIn("product_b_sku", data)
        self.assertEqual(data["product_b_sku"], recommendation.product_b_sku)
        self.assertIn("type", data)
        self.assertEqual(data["type"], recommendation.type.name)

    def test_deserialize_recommendation(self):
        """It should de-serialize a Recommendation"""
        data = RecommendationFactory().serialize()
        recommendation = Recommendation()
        recommendation.deserialize(data)
        self.assertNotEqual(recommendation, None)
        self.assertEqual(recommendation.id, None)
        self.assertEqual(recommendation.product_a_sku, data["product_a_sku"])
        self.assertEqual(recommendation.product_b_sku, data["product_b_sku"])
        self.assertEqual(recommendation.type, getattr(RecommendationType, data["type"]))

    def test_deserialize_missing_data(self):
        """It should not deserialize a Recommendation with missing data"""
        data = {"id": 1, "product_a_sku": "AA", "product_b_sku": "BB"}
        recommendation = Recommendation()
        self.assertRaises(DataValidationError, recommendation.deserialize, data)

    def test_deserialize_bad_data(self):
        """It should not deserialize bad data"""
        data = "this is not a dictionary"
        recommendation = Recommendation()
        self.assertRaises(DataValidationError, recommendation.deserialize, data)

    def test_deserialize_long_sku(self):
        """It should not deserialize too long SKU attribute"""
        test_recommendation = RecommendationFactory()
        data = test_recommendation.serialize()
        data["product_a_sku"] = "AAAAAAAAAAA"
        recommendation = Recommendation()
        self.assertRaises(DataValidationError, recommendation.deserialize, data)

        # same check for product b
        data["product_a_sku"] = "A"
        data["product_b_sku"] = "BBBBBBBBBBB"
        recommendation = Recommendation()
        self.assertRaises(DataValidationError, recommendation.deserialize, data)

    def test_deserialize_bad_type(self):
        """It should not deserialize a bad type attribute"""
        test_recommendation = RecommendationFactory()
        data = test_recommendation.serialize()
        data["type"] = "cross_sale"  # wrong case
        recommendation = Recommendation()
        self.assertRaises(DataValidationError, recommendation.deserialize, data)


######################################################################
#  T E S T   E X C E P T I O N   H A N D L E R S
######################################################################
class TestExceptionHandlers(TestCaseBase):
    """Recommendation Model Exception Handlers"""

    @patch("service.models.db.session.commit")
    def test_create_exception(self, exception_mock):
        """It should catch a create exception"""
        exception_mock.side_effect = Exception()
        recommendation = RecommendationFactory()
        self.assertRaises(DataValidationError, recommendation.create)

    @patch("service.models.db.session.commit")
    def test_update_exception(self, exception_mock):
        """It should catch a update exception"""
        exception_mock.side_effect = Exception()
        recommendation = RecommendationFactory()
        self.assertRaises(DataValidationError, recommendation.update)

    @patch("service.models.db.session.commit")
    def test_delete_exception(self, exception_mock):
        """It should catch a delete exception"""
        exception_mock.side_effect = Exception()
        recommendation = RecommendationFactory()
        self.assertRaises(DataValidationError, recommendation.delete)


######################################################################
#  Q U E R Y   T E S T   C A S E S
######################################################################
class TestModelQueries(TestCaseBase):
    """Recommendation Model Query Tests"""

    def test_find_recommendation(self):
        """It should Find a Recommendation by ID"""
        recommendations = RecommendationFactory.create_batch(5)
        for recommendation in recommendations:
            recommendation.create()
        logging.debug(recommendations)
        # make sure they got saved
        self.assertEqual(len(Recommendation.all()), 5)
        # find the 2nd pet in the list
        recommendation = Recommendation.find(recommendations[1].id)
        self.assertIsNot(recommendation, None)
        self.assertEqual(recommendation.id, recommendations[1].id)
        self.assertEqual(recommendation.product_a_sku, recommendations[1].product_a_sku)
        self.assertEqual(recommendation.product_b_sku, recommendations[1].product_b_sku)
        self.assertEqual(recommendation.type, recommendations[1].type)
