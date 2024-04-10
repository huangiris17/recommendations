Feature: The recommendation service back-end
    As a Recommendation Manager
    I need a RESTful catalog service
    So that I can keep track of all recommendations

    Background:
        Given the following Recommendations
            | product_a_sku | product_b_sku | recommendation_type | likes |
            | HYJtLnYf      | cUnyEDwP      | CROSS_SELL          | 0     |

    Scenario: The server is running
        When I visit the "Home Page"
        Then I should see "Recommendation RESTful Service" in the title
        And I should not see "404 Not Found"

    Scenario: Retrieve recommendation
        When I visit the "Home Page"
        And I set the "Id" to "221"
        And I press the "Retrieve" button
        Then I should see the message "Success"
        And I should see "HYJtLnYf" in the "Product a sku" field
        And I should see "cUnyEDwP" in the "Product b sku" field
        And I should see "CROSS_SELL" in the "Recommendation type" field
        And I should see "0" in the "Likes" field
