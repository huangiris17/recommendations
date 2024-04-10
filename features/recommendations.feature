Feature: The recommendation service back-end
    As a Recommendation Manager
    I need a RESTful catalog service
    So that I can keep track of all recommendations

Background:
    Given the following Recommendations
        | product_a_sku | product_b_sku | recommendation_type  | likes |
        | HYJtLnYf      | cUnyEDwP      | CROSS_SELL    | 0 |
        | GQGEsdfq      | cUafQfef      | CROSS_SELL    | 0 |
        | FQEFQrQs      | cEdasdTs      | UP_SELL       | 1 |
        | dasdfeaQ      | FefaffeQ      | BUNDLE        | 3 |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Recommendation RESTful Service" in the title
    And I should not see "404 Not Found"

Scenario: Search for HYJtLnYf
    When I visit the "Home Page"
    And I set the "Product A SKU" to "HYJtLnYf"
    And I press the "Search" button
    Then I should see the message "Success"
    # And I should see "HYJtLnYf" in the results
    And I should not see "cEdasdTs" in the results
    And I should not see "FefaffeQ" in the results

Scenario: Search for UP_SELL
    When I visit the "Home Page"
    And I select "UP_SELL" in the "Recommendation type" dropdown
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "cEdasdTs" in the results
    And I should not see "cUnyEDwP" in the results
    And I should not see "FefaffeQ" in the results

Scenario: Search for dasdfeaQ and BUNDLE
    When I visit the "Home Page"
    And I set the "Product A SKU" to "dasdfeaQ"
    And I select "BUNDLE" in the "Recommendation type" dropdown
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "FefaffeQ" in the results
    And I should not see "cUnyEDwP" in the results
    And I should not see "cEdasdTs" in the results