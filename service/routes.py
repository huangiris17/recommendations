######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

# spell: ignore Rofrano jsonify restx dbname
"""
Recommendation Store Service

This service implements a REST API that allows you to Create, Read, Update
and Delete Recommendations from the inventory of recommendations in the RecommendationShop
"""

from flask import jsonify, request, url_for, abort
from flask import current_app as app  # Import Flask
from flask_restx import Resource, fields, reqparse, inputs
from service.models import Recommendation, RecommendationType
from service.common import status  # HTTP Status Codes
from . import api


######################################################################
# GET HEALTH CHECK
######################################################################
@app.route("/health")
def health_check():
    """Let them know our heart is still beating"""
    return jsonify(status=200, message="Healthy"), status.HTTP_200_OK


######################################################################
# GET INDEX
######################################################################
# @app.route("/")
# def index():
#     """Root URL response"""
#     return (
#         jsonify(
#             name="Recommendations REST API Service",
#             version="1.0",
#             paths=[
#                 (
#                     {
#                         "path": str(rule),
#                         "methods": list(rule.methods),
#                         "description": globals()[rule.endpoint].__doc__,
#                     }
#                 )
#                 for rule in app.url_map.iter_rules()
#                 if rule.endpoint != "static"
#             ],
#         ),
#         status.HTTP_200_OK,
#     )


######################################################################
# Configure the Root route before OpenAPI
######################################################################
@app.route("/")
def index():
    """Index page"""
    return app.send_static_file("index.html")


# Define the model so that the docs reflect what can be sent
create_model = api.model(
    "Recommendation",
    {
        "product_a_sku": fields.String(
            required=True,
            description="String with no more than 10 characters, can not be null, represents product a",
        ),
        "product_b_sku": fields.String(
            required=True,
            description="String with no more than 10 characters, can not be null, represents product b",
        ),
        # pylint: disable=protected-access
        "recommendation_type": fields.String(
            enum=RecommendationType._member_names_,
            description='one of {"UP_SELL", "CROSS_SELL", "ACCESSORY", "BUNDLE"},\
                denotes the relationship between product a and product b',
        ),
        "likes": fields.int(
            required=True,
            description="Integer no less than 0, reflects the popularity of a recommendation",
        ),
    },
)

recommendation_model = api.inherit(
    "RecommendationModel",
    create_model,
    {"id": fields.int(readOnly=True, description="Integer, serves as the primary key")},
)

# query string arguments
recommendation_args = reqparse.RequestParser()
recommendation_args.add_argument(
    "product_a_sku", type=str, location="args", required=False,
    help="String with no more than 10 characters, can not be null, represents product a"
)
recommendation_args.add_argument(
    "recommendation_type", type=str, location="args", required=False,
    help='one of {"UP_SELL", "CROSS_SELL", "ACCESSORY", "BUNDLE"}, denotes the relationship between product a and product b'
)


######################################################################
#  PATH: /pets/{id}
######################################################################
@api.route("/recommendations/<int:recommendation_id>")
@api.param("recommendation_id", "The Recommendation identifier")
class RecommendationResource(Resource):
    """
    RecommendationResource class

    Allows the manipulation of a single Recommendation
    GET /recommendation{id} - Returns a Recommendation with the id
    PUT /recommendation{id} - Updates a Recommendation with the id
    DELETE / recommendation{id} - Deletes a Recommendation with the id
    """

    # ------------------------------------------------------------------
    # RETRIEVE A RECOMMENDATION
    # ------------------------------------------------------------------
    @api.doc("get_recommendations")
    @api.response(404, "Recommendation with id not found")
    @api.marshal_with(recommendation_model)
    def get(self, recommendation_id):
        """
        Retrieves a single Recommendation

        This endpoint will return a Recommendation based on its id
        """

        app.logger.info("Request for recommendation with id: %s", recommendation_id)

        recommendation = Recommendation.find(recommendation_id)
        if not recommendation:
            error(
                status.HTTP_404_NOT_FOUND,
                f"Recommendation with id '{recommendation_id}' was not found.",
            )

        app.logger.info("Returning recommendation: %s", recommendation.name)
        return jsonify(recommendation.serialize()), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # UPDATE AN EXISTING RECOMMENDATION
    # ------------------------------------------------------------------
    @api.doc("update_recommendations")
    @@api.response(404, "Recommendation with id not found")
    @api.response(400, "The posted Recommendation data was not valid")
    @api.expect(recommendation_model)
    @api.marshal_with(recommendation_model)
    def put(self, recommendation_id):
        """
        Updates a Recommendation

        This endpoint will update a Recommendation based on the body that is posted
        """
        app.logger.info("Request to update recommendation with id: %d", recommendation_id)
        check_content_type("application/json")

        recommendation = Recommendation.find(recommendation_id)
        if not recommendation:
            error(
                status.HTTP_404_NOT_FOUND,
                f"Recommendation with id: '{recommendation_id}' was not found.",
            )

        recommendation.deserialize(request.get_json())
        recommendation.id = recommendation_id
        recommendation.update()

        app.logger.info("Recommendation with ID: %d updated.", recommendation.id)
        return jsonify(recommendation.serialize()), status.HTTP_200_OK

    ######################################################################
    # DELETE A RECOMMENDATION
    ######################################################################
    @api.doc("delete_recommendations")
    @api.response(204, "Recommendation deleted")
    def delete_recommendations(recommendation_id):
        """
        Deletes a Recommendation

        This endpoint will delete a Recommendation based the id specified in the path
        """
        app.logger.info("Request to delete recommendation with id: %d", recommendation_id)

        recommendation = Recommendation.find(recommendation_id)
        if recommendation:
            recommendation.delete()
            app.logger.info("Recommendation with ID: %d was deleted.", recommendation_id)

        return "", status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /recommendations
######################################################################
@api.route("recommendations", strict_slashes=False)
class RecommendationCollection(Resource):
    """Handles all interactions with collections of Recommendations"""

    ######################################################################
    # LIST ALL RECOMMENDATIONS
    ######################################################################
    @api.doc("list_recommendations")
    @api.expect(recommendation_args, validate=True)
    @api.marshal_list_with(recommendation_model)
    def get(self):
        """Returns all of the Recommendations"""
        app.logger.info("Request for recommendation list")

        recommendations = []
        args = recommendation_args.parse_args()
        # See if any query filters were passed in
        a_sku = args["product_a_sku"]
        recommendation_type = args["recommendation_type"]

        if a_sku and recommendation_type:
            type_value = getattr(RecommendationType, recommendation_type.upper())
            recommendations = Recommendation.find_by_product_a_sku_and_type(
                a_sku, type_value
            )
        elif a_sku:
            recommendations = Recommendation.find_by_product_a_sku(a_sku)
        elif recommendation_type:
            type_value = getattr(RecommendationType, recommendation_type.upper())
            recommendations = Recommendation.find_by_type(type_value)
        else:
            recommendations = Recommendation.all()

        results = [recommendation.serialize() for recommendation in recommendations]
        app.logger.info("Returning %d recommendations", len(results))
        return jsonify(results), status.HTTP_200_OK


    ######################################################################
    # CREATE A NEW RECOMMENDATION
    ######################################################################
    @api.doc("create_recommendation")
    @api.response(400, "The posted data was not valid")
    @api.response(415, "Content-Type must be application/json")
    @api.response(409, "Duplicate recommendation detected.")
    @api.expect(create_model)
    @api.marshal_with(recommendation_model, code=201)
    def post(self):
        """
        Creates a Recommendation
        This endpoint will create a Recommendation based on the data in the body that is posted
        """
        app.logger.info("Request to create a recommendation")
        check_content_type("application/json")

        recommendation = Recommendation()
        recommendation.deserialize(request.get_json())

        if recommendation.exists():
            error(status.HTTP_409_CONFLICT, "Duplicate recommendation detected.")

        recommendation.create()
        message = recommendation.serialize()
        location_url = url_for(
            "get_recommendations", recommendation_id=recommendation.id, _external=True
        )

        app.logger.info("Recommendation %d created.", recommendation.id)
        return (
            jsonify(message),
            status.HTTP_201_CREATED,
            {"Location": location_url},
        )


######################################################################
#  PATH: /recommendations/{id}/like
######################################################################
@api.route("recommendations/<recommendation_id>/like")
@api.param("recommendation_id", "The Recommendation Identifier")
class LikeResource(Resource):
    """Like actions on a pet"""

    ######################################################################
    # INCREMENT LIKES FIELD FOR A RECOMMENDATION
    ######################################################################
    @api.doc("like_recommendations")
    @api.response(404, "Recommendation with id was not found.")
    def put(self, recommendation_id):
        """
        Increments likes for a Recommendation.

        This endpoint will increment the likes for the Recommendation with ID specified in URL
        """
        app.logger.info(
            "Request to increment recommendation's likes field with id: %d",
            recommendation_id,
        )

        recommendation = Recommendation.find(recommendation_id)
        if not recommendation:
            error(
                status.HTTP_404_NOT_FOUND,
                f"Recommendation with id: '{recommendation_id}' was not found.",
            )

        recommendation.add_like()

        app.logger.info(
            "Recommendation with ID: %d - likes field incremented.", recommendation.id
        )
        return jsonify(recommendation.serialize()), status.HTTP_200_OK

    ######################################################################
    # DECREMENT LIKES FIELD FOR A RECOMMENDATION
    ######################################################################
    @api.doc("dislike_recommendations")
    @api.response(404, "Recommendation with id was not found.")
    def delete(self, recommendation_id):
        """
        Decrements likes for a Recommendation.

        This endpoint will decrement the likes for the Recommendation with ID specified in URL
        """
        app.logger.info(
            "Request to decrement recommendation's likes field with id: %d",
            recommendation_id,
        )

        recommendation = Recommendation.find(recommendation_id)
        if not recommendation:
            error(
                status.HTTP_404_NOT_FOUND,
                f"Recommendation with id: '{recommendation_id}' was not found.",
            )

        recommendation.remove_like()

        app.logger.info(
            "Recommendation with ID: %d - likes field decremented.", recommendation.id
        )
        return jsonify(recommendation.serialize()), status.HTTP_200_OK


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


######################################################################
# Checks the ContentType of a request
######################################################################
def check_content_type(content_type):
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        error(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    error(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )


######################################################################
# Logs error messages before aborting
######################################################################
def error(status_code, reason):
    """Logs the error and then aborts"""
    app.logger.error(reason)
    abort(status_code, reason)
