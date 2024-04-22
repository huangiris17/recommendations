"""
Environment for Behave Testing
"""

from os import getenv
from selenium import webdriver

WAIT_SECONDS = int(getenv("WAIT_SECONDS", "60"))
PORT = getenv("PORT", "8000")
ROOT_URL = getenv("BASE_URL", f"http://localhost:{PORT}")
BASE_URL = getenv("BASE_URL", f"http://localhost:{PORT}/api")
DRIVER = getenv("DRIVER", "firefox").lower()


def before_all(context):
    """Executed once before all tests"""
    context.root_url = ROOT_URL
    context.base_url = BASE_URL
    context.wait_seconds = WAIT_SECONDS
    # Select either Chrome or Firefox
    if "firefox" in DRIVER:
        context.driver = get_firefox()
    else:
        context.driver = get_chrome()
    context.driver.implicitly_wait(context.wait_seconds)
    context.config.setup_logging()


def after_all(context):
    """Executed after all tests"""
    context.driver.quit()


######################################################################
# Utility functions to create web drivers
######################################################################


def get_chrome():
    """Creates a headless Chrome driver"""
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--headless")
    return webdriver.Chrome(options=options)


def get_firefox():
    """Creates a headless Firefox driver"""
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")
    return webdriver.Firefox(options=options)
