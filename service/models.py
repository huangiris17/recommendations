"""
Models for Recommendation

All of the models are stored in this module
"""

import logging
from enum import Enum
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""


class PrimaryKeyNotSetError(Exception):
    """Used when tried to set primary key to None"""


class TextColumnLimitExceededError(Exception):
    """Used when column character limit has been exceeded"""


class RecommendationType(Enum):
    """Enum representing types of recommendation"""

    UP_SELL = "UP_SELL"
    CROSS_SELL = "CROSS_SELL"
    ACCESSORY = "ACCESSORY"
    BUNDLE = "BUNDLE"


SKU_CHAR_LIMIT = 10


class Recommendation(db.Model):
    """
    Class that represents a Recommendation
    """

    ##################################################
    # Table Schema
    ##################################################
    id = db.Column(db.Integer, primary_key=True)
    product_a_sku = db.Column(db.String(SKU_CHAR_LIMIT), nullable=False)
    product_b_sku = db.Column(db.String(SKU_CHAR_LIMIT), nullable=False)
    recommendation_type = db.Column(db.Enum(RecommendationType), nullable=False)
    likes = db.Column(db.Integer, nullable=False, default=0)

    name = f"{product_a_sku}-{product_b_sku}"

    def __repr__(self):
        return (
            f"<Recommendation {self.product_a_sku}-{self.product_b_sku} id=[{self.id}]>"
        )

    def create(self):
        """
        Creates a Recommendation to the database
        """
        logger.info("Creating %s", self.name)
        self.id = None  # pylint: disable=invalid-name
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error creating record: %s", self)
            raise DataValidationError(e) from e

    def update(self):
        """
        Updates a Recommendation to the database
        """
        logger.info("Saving %s", self.name)
        try:
            if self.id is None:
                # don't allow primary key to be set to None
                raise PrimaryKeyNotSetError()

            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error updating record: %s", self)
            raise DataValidationError(e) from e

    def delete(self):
        """Removes a Recommendation from the data store"""
        logger.info("Deleting %s", self.name)
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error deleting record: %s", self)
            raise DataValidationError(e) from e

    def serialize(self):
        """Serializes a Recommendation into a dictionary"""
        return {
            "id": self.id,
            "product_a_sku": self.product_a_sku,
            "product_b_sku": self.product_b_sku,
            "recommendation_type": self.recommendation_type.name,
            "likes": self.likes,
        }

    def deserialize(self, data):
        """
        Deserializes a Recommendation from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            if len(data["product_a_sku"]) > SKU_CHAR_LIMIT:
                raise TextColumnLimitExceededError("product_a_sku")
            self.product_a_sku = data["product_a_sku"]

            if len(data["product_b_sku"]) > SKU_CHAR_LIMIT:
                raise TextColumnLimitExceededError("product_b_sku")
            self.product_b_sku = data["product_b_sku"]
            self.recommendation_type = getattr(
                RecommendationType, data["recommendation_type"]
            )  # create enum from string

            if isinstance(data["likes"], int):
                self.likes = data["likes"]
            else:
                raise DataValidationError(
                    "Invalid type for integer [likes]: " + str(type(data["likes"]))
                )
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid Recommendation: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Recommendation: body of request contained bad or no data "
                + str(error)
            ) from error
        except TextColumnLimitExceededError as error:
            raise DataValidationError(
                "Invalid Recommendation: exceeded maximum character limit at column: "
                + str(error)
            ) from error

        return self

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def all(cls):
        """Returns all of the Recommendations in the database"""
        logger.info("Processing all Recommendations")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Finds a Recommendation by it's ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return db.session.get(cls, by_id)

    @classmethod
    def find_by_product_a_sku(cls, sku):
        """Returns all Recommendations with the given product a sku

        Args:
            sku (string): the sku of product A in the Recommendations you want to match
        """
        logger.info("Processing product a sku query for %s ...", sku)
        return cls.query.filter(cls.product_a_sku == sku)

    @classmethod
    def find_by_product_b_sku(cls, sku):
        """Returns all Recommendations with the given product b sku

        Args:
            sku (string): the sku of product B in the Recommendations you want to match
        """
        logger.info("Processing product b sku query for %s ...", sku)
        return cls.query.filter(cls.product_b_sku == sku)

    @classmethod
    def find_by_type(cls, recommendation_type: RecommendationType) -> list:
        """Returns all Recommendations by their Type

        :param recommendation_type: RecommendationType
        :recommendation_type available: enum

        :return: a collection of Recommendations that are of requested type
        :rtype: list

        """
        logger.info("Processing type query for %s ...", recommendation_type.name)
        return cls.query.filter(cls.recommendation_type == recommendation_type)
