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

"""
Recommendation Store Service

This service implements a REST API that allows you to Create, Read, Update
and Delete Recommendations from the inventory of recommendations in the RecommendationShop
"""

from flask import jsonify, request, url_for, abort
from flask import current_app as app  # Import Flask application
from service.models import Recommendation, RecommendationType
from service.common import status  # HTTP Status Codes


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return (
        "Reminder: return some useful information in json format about the service here",
        status.HTTP_200_OK,
    )


######################################################################
# LIST ALL RECOMMENDATIONS
######################################################################
@app.route("/recommendations", methods=["GET"])
def list_recommendations():
    """Returns all of the recommendations"""
    app.logger.info("Request for recommendation list")

    recommendations = []
    recommendations = Recommendation.all()

    results = [recommendation.serialize() for recommendation in recommendations]
    app.logger.info("Returning %d recommendations", len(results))
    return jsonify(results), status.HTTP_200_OK


######################################################################
# CREATE A NEW RECOMMENDATION
######################################################################
@app.route("/recommendations", methods=["POST"])
def create_recommendation():
    """
    Creates a Recommendation
    This endpoint will create a Recommendation based on the data in the body that is posted
    """
    app.logger.info("Request to create a recommendation")
    check_content_type("application/json")

    data = request.get_json()
    try:
        recommendation_type = RecommendationType[data.get("type")]
    except KeyError:
        error(status.HTTP_400_BAD_REQUEST, "Invalid recommendation type.")

    existing_recommendation = Recommendation.query.filter_by(
        product_a_sku=data.get("product_a_sku"),
        product_b_sku=data.get("product_b_sku"),
        type=recommendation_type,
    ).first()

    if existing_recommendation:
        error(status.HTTP_400_BAD_REQUEST, "Duplicate recommendation detected.")

    recommendation = Recommendation()
    recommendation.deserialize(request.get_json())
    recommendation.create()
    message = recommendation.serialize()
    location_url = url_for(
        "get_recommendationss", recommendation_id=recommendation.id, _external=True
    )

    app.logger.info("Recommendation %d created.", recommendation.id)
    return (
        jsonify(message),
        status.HTTP_201_CREATED,
        {"Location": location_url},
    )


######################################################################
# READ A RECOMMENDATION
######################################################################
@app.route("/recommendations/<int:recommendation_id>", methods=["GET"])
def get_recommendationss(recommendation_id):
    """
    Retrieves a single Recommendation

    This endpoint will return a Recommendation based on it's id
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


######################################################################
# DELETE A RECOMMENDATION
######################################################################
@app.route("/recommendations/<int:recommendation_id>", methods=["DELETE"])
def delete_recommendations(recommendation_id):
    """
    Deletes a Recommendation

    This endpoint will delete a Recommendation based the id specified in the path
    """
    app.logger.info("Request to delete recommendation with id: %d", recommendation_id)

    recommendation = Recommendation.find(recommendation_id)
    if recommendation:
        recommendation.delete()

    app.logger.info("Recommendation with ID: %d delete complete.", recommendation_id)
    return "", status.HTTP_204_NO_CONTENT


######################################################################
# UPDATE AN EXISTING RECOMMENDATION
######################################################################
@app.route("/recommendations/<int:recommendation_id>", methods=["PUT"])
def update_recommendations(recommendation_id):
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
