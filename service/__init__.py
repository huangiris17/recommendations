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

"""
Package: service
Package for the application models and service routes
This module creates and configures the Flask app and sets up the logging
and SQL database
"""
import sys
from flask import Flask
from flask_restx import Api
from service import config
from service.common import log_handlers

# NOTE: Do not change the order of this code
# The Flask app must be created
# BEFORE you import modules that depend on it !!!

# Will be initialize when app is created
api = None  # pylint: disable=invalid-name


############################################################
# Initialize the Flask instance
############################################################
def create_app():
    """Initialize the core application."""
    # Create Flask application
    app = Flask(__name__)
    app.config.from_object(config)

    # Turn off strict slashes because it violates best practices
    app.url_map.strict_slashes = False

    ######################################################################
    # Configure Swagger before initializing it
    ######################################################################
    global api
    api = Api(
        app,
        version="1.0.0",
        title="Recommendation REST API Service",
        description="This is a sample server Recommendation server.",
        default="Recommendations",
        default_label="Recommendation operations",
        doc="/apidocs",  # default also could use doc='/apidocs/'
        # authorizations=authorizations,
        prefix="/api",
    )

    with app.app_context():
        # Import the routes After the Flask app is created
        # pylint: disable=import-outside-toplevel
        # pylint: disable=unused-import
        # pylint: disable=cyclic-import
        from service import routes, models  # noqa: F401, E402
        from service.common import error_handlers
        from service.models import db

        db.init_app(app)

        try:
            db.create_all()
        except Exception as error:  # pylint: disable=broad-except
            app.logger.critical("%s: Cannot continue", error)
            # gunicorn requires exit code 4 to stop spawning workers when they die
            sys.exit(4)

        # Set up logging for production
        log_handlers.init_logging(app, "gunicorn.error")

        app.logger.info(70 * "*")
        app.logger.info(
            "  R E C O M M E N D A T I O N   S E R V I C E   R U N N I N G  ".center(
                70, "*"
            )
        )
        app.logger.info(70 * "*")

        app.logger.info("Service initialized!")

        return app
