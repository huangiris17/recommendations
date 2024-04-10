Feature: The recommendation service back-end
    As a Recommendation Manager
    I need a RESTful catalog service
    So that I can keep track of all recommendations

Background:
    Given the following Recommendations
        | product_a_sku | product_b_sku | recommendation_type  | likes |
        | HYJtLnYf      | cUnyEDwP      | CROSS_SELL    | 0 |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Recommendation RESTful Service" in the title
    And I should not see "404 Not Found"