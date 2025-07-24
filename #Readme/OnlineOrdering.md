# Testing
    * Create session
        * Working. Had to add a Name to the login requerst. Made it "Online Ordering: <Username>".
    * Set your brand to one of the brands that you're enabled for (you get the list in the create session response) list stores

    * Pick a store from the list
    * View store
    * Find the menu id for the store you chose in the response data
    * View menu
    * Place order - you'll probably need to tweak the request to use the right set of plu codes and prices and whatever

# Localhost
    dhiren2 / MPZe5odqRFD3wkHcBMa0a6FXfRhniBH62qnb

# Prod
    cosofttest / 3SEql7msL57VQyAMqgpVvnwkp5xGHT/oXyYb





# Test
    * CreateLoginForIntegrationPartnerAsync
        * This creates an IntegrationPartnerLoginMap record and uses UserId. Check when creating that UserId is set.
        * MediatorManager.HandleSearchOrdersRequestAsync : authenticatedUserId


