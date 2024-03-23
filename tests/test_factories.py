"""
Test Cases for Factories
"""

from unittest import TestCase
from tests.factories import RecommendationFactory
from service.models import RecommendationType


# pylint: disable=too-many-public-methods
class TestFactories(TestCase):
    """Test Cases for Factories"""

    def test_recommendation_factory_creation(self):
        """It should return recommendation with random data"""
        recommendation = RecommendationFactory()
        self.assertTrue(recommendation is not None)
        self.assertTrue(recommendation.id is not None)
        self.assertTrue(recommendation.product_a_sku is not None)
        self.assertTrue(recommendation.product_b_sku is not None)
        self.assertTrue(recommendation.recommendation_type in RecommendationType)
