Feature: The recommendation service back-end
    As a Recommendation Manager
    I need a RESTful catalog service
    So that I can keep track of all recommendations

    Background:
        Given the following Recommendations
            | product_a_sku | product_b_sku | recommendation_type | likes |
            | HYJtLnYf      | cUnyEDwP      | CROSS_SELL          | 0     |
            | GQGEsdfq      | cUafQfef      | CROSS_SELL          | 0     |
            | FQEFQrQs      | cEdasdTs      | UP_SELL             | 1     |
            | dasdfeaQ      | FefaffeQ      | BUNDLE              | 3     |

    Scenario: The server is running
        When I visit the "Home Page"
        Then I should see "Recommendation RESTful Service" in the title
        And I should not see "404 Not Found"

    Scenario: Search for HYJtLnYf
        When I visit the "Home Page"
        And I press the "Clear" button
        And I set the "Product A SKU" to "HYJtLnYf"
        And I press the "Search" button
        Then I should see the message "Success"
        And I should see "HYJtLnYf" in the results
        And I should not see "cEdasdTs" in the results
        And I should not see "FefaffeQ" in the results
        And I should not see "cUafQfef" in the results

    Scenario: Search for UP_SELL
        When I visit the "Home Page"
        And I press the "Clear" button
        And I select "UP_SELL" in the "Recommendation type" dropdown
        And I press the "Search" button
        Then I should see the message "Success"
        And I should see "cEdasdTs" in the results
        And I should not see "cUnyEDwP" in the results
        And I should not see "cUafQfef" in the results
        And I should not see "FefaffeQ" in the results

    Scenario: Search for dasdfeaQ and BUNDLE
        When I visit the "Home Page"
        And I press the "Clear" button
        And I set the "Product A SKU" to "dasdfeaQ"
        And I select "BUNDLE" in the "Recommendation type" dropdown
        And I press the "Search" button
        Then I should see the message "Success"
        And I should see "FefaffeQ" in the results
        And I should not see "cUnyEDwP" in the results
        And I should not see "cEdasdTs" in the results
        And I should not see "cUafQfef" in the results

    Scenario: Search for nonexistent recommendation: AfqrQtgQ
        When I visit the "Home Page"
        And I press the "Clear" button
        And I set the "Product A SKU" to "AfqrQtgQ"
        And I press the "Search" button
        Then I should see the message "Success"
        And I should not see "HYJtLnYf" in the results
        And I should not see "cEdasdTs" in the results
        And I should not see "FefaffeQ" in the results
        And I should not see "cUafQfef" in the results

    Scenario: Create a Recommendation
        When I visit the "Home Page"
        And I set the "product_a_sku" to "Product_a"
        And I set the "product_b_sku" to "Product_b"
        And I select "CROSS_SELL" in the "recommendation_type" dropdown
        And I press the "Create" button
        Then I should see the message "Successfully created a recommendation"
        When I press the "Clear" button
        Then the "id" field should be empty
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

    Scenario: Retrieve recommendation
        When I visit the "Home Page"
        And I set the "Id" to "221"
        And I press the "Retrieve" button
        Then I should see the message "Success"
        And I should see "HYJtLnYf" in the "Product a sku" field
        And I should see "cUnyEDwP" in the "Product b sku" field
        And I should see "CROSS_SELL" in the "Recommendation type" field
        And I should see "0" in the "Likes" field
