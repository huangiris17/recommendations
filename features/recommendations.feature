Feature: The recommendation service back-end
    As a Recommendation Manager
    I need a RESTful catalog service
    So that I can keep track of all recommendations

Background:
    Given the following Recommendations
        | id | product_a_sku | product_b_sku | recommendation_type  | likes |
        | 10 | HYJtLnYf      | cUnyEDwP      | CROSS_SELL    | 0 |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Recommendation RESTful Service" in the title
    And I should not see "404 Not Found"

Scenario: Create a Recommendation
    When I visit the "Home Page"
    And I set the "product_a_sku" to "Product_a"
    And I set the "product_b_sku" to "Product_b"
    And I select "CROSS_SELL" in the "recommendation_type" dropdown
    And I press the "Create" button
    Then I should see the message "Successfully created a recommendation"
    When I copy the "recommendation_id" field
    And I press the "Clear" button
    Then the "recommendation_id" field should be empty
    And the "product_a_sku" field should be empty
    And the "product_b_sku" field should be empty
    And the "recommendation_type" field should be empty
    And the "likes" field should be empty
    When I visit the "Home Page"
    And I set the "product_a_sku" to "Product_a"
    And I set the "product_b_sku" to "Product_b"
    And I select "CROSS_SELL" in the "recommendation_type" dropdown
    And I press the "Create" button
    Then I should see the message "409 Conflict: Duplicate recommendation detected."
    # --uncomment when Retrieve button set--
    # When I paste the "recommendation_id" field
    # And I press the "Retrieve" button
    # Then I should see the message "Success"
    # And I should see "Product_a" in the "product_a_sku" field
    # And I should see "Product_b" in the "product_b_sku" field
    # And I should see "CROSS_SELL" in the "recommendation_type" dropdown
    # And I should see "0" in the "likes" field