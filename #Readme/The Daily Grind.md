# PERSONAL
* Hospital stuff.
	* Hospital claimed 47,797.90 and was paid 47,634.81. Must pay R163.09.		
* Book car service. Arno's auto services.
	* http://arnoldsautoserviceshilton.co.za/Pages/Contact-Us.asp




## -------------------------------------------------------------
# Done
## Bugs




## UI




## New
- Hide disabled sales channels in the report param multiselect.



## Misc




## -----------------------------------------------------------------------------------
## -----------------------------------------------------------------------------------
# Busy on	
- CompanionGrvStuff to prod.
	


## To-Do


- MenuItemRecipeMap.Quantity update to Prod.
	- Check Portal too. Must handle a decimal quantity.

- Stocktake columns to prod. 

- Make GRV's nullable until locking or finalising - and then apply the rules.
	- Remove columns not in use anywhere.
	- New GRV transaction type must default to GRV. Might need to make this optional.
	- Add GrvItem.Order. Default ordering of grv items to be Order, then Item code (think it's currently item code)
	- Make ItemId, UnitQuantity, UnitOfMeasure, UnitTotalCost, UnitTotalCostIncl, UnitTotalTaxes nullable and update where used.
		- Include these in rules for locking/receiving/returning.
	- Check GP stuff out


- Stocktake: When creating a new subcount, if it exists already but is archived an exception is raised. Rather unarchive it, and return the Id as though it was created.

- hotfix/hide-disabled-sales-channels : Did a dirty hack to hide disabled sales channels in the portal reports. Need to return to this and to it properly in the API and change SalesChannel.IsEnabled to .IsArchived.

- Roles names in user lookup should include (s) and (b) for store or brand level.

- User: Roles combo is not working as expected. Need to be able to assign a user to multiple stores. The stand-alone popup does it, so the logic is there.
- Users: The grid should reflect None in the permission count columns if not enabled for those.

- Reports: Ability to get just the list of categories - no reports.

- https://cosoft.slack.com/archives/C05QKC26U1G/p1753096403063719
	- JP says when his store is selected, not all stock items show for the brand.

- Stocklists: Itemcount includes archived items.

https://bitbucket.org/cosoft-ondemand/cloud_backend/pull-requests/1886/overview


- Reports: Ability to star a report (favourite)

- Users Bug.
	- Using leigh.morum@gmail.com, but should happen with any user.
	- Select South Africa / Leigh's Coffee Brand / Leigh's Coffee [Leigh2]
	- Put leigh.morum@gmail.com in the search. Results are as expected.
	- Remove leigh.morum@gmail.com from the search again, pages of users are returned. BUG.

	- Need an index on GRV Store, TransactionType, Status.

- GRV
	- Check GP functionality
		- Endpoints
			- ExternalDataFeedController				
			- ReportsController

		- Aura.Manager.ExternalDataQuery/PurchaseQueryManager.cs
			- Used by ExternalDataFeedController
		- Aura.Manager.ExternalDataQuery/ReturnQueryManager.cs
			- Used by ExternalDataFeedController
		- Aura.Manager.Stock/Reports/ActualUsageCalculator.cs
			- Used by GrossProfitReportManager and StockLossReportManager		
		- Aura.Manager.Stock/Reports/GrossProfitReportManager.cs
			- Used by ReportsController

			- var totalPurchases = receives.Where(x => x.Grv.GrvTransactionTypeId == (int)AuraCloudInterface.Stock.Grv.GrvTransactionType.Grv).Sum(x => x.UnitTotalCost);
        	- var totalReturns = receives.Where(x => x.Grv.GrvTransactionTypeId != (int)AuraCloudInterface.Stock.Grv.GrvTransactionType.Grv).Sum(x => x.UnitTotalCost);
			- PurchasesUnits = receives.Where(x => x.Grv.GrvTransactionTypeId == (int)AuraCloudInterface.Stock.Grv.GrvTransactionType.Grv).Sum(x => x.UnitQuantity) * (100M - storeWastagePercentage) / 100M,
		- Aura.Manager.Stock/Reports/StockLossReportManager.cs
			- Used by ReportsController
		- Aura.Manager.Stock/Reports/TheoreticalSalesReportManager.cs
			- Used by ReportsController, GrossProfitReportManager, StockLossReportManager, TheoreticalStockOnHandManager

			- await readOnlyStockContext.Grvs.Where(x => x.StoreId == openingStockTake.StoreId && x.GrvDate >= openingStockTake.DateTime && x.GrvStatusId == (int)AuraCloudInterface.Stock.Grv.GrvStatus.Finalized).ToListAsync(),
				- Should x.GrvDate not be x.StockMovementAt?
		- TheoreticalStockOnHandManager				
			- Used by ReportsController				
	



- Ability to move a payment into the background.
	- Stop syncing of docs automatically unless payment is set to isBackgrounded.
	- Endpoint to background a payment transaction.




- https://cosoft.atlassian.net/browse/API-685 : Auditing
	- AuditManager needs nullable userId and nullable CorrelationId.
	- AuditManager must lookup userId and correlationId itsself when logging.
	- What about monitoring entity framework somehow, and when data is committed, try to pickup the before/after and log automagically?
		- If this can work, then we can decorate entities with a custom attribute to indicate no auditing or something. Or by default, no auditing unless a specific attribute. Something like that.

- Permissions so Leigh can get a list of permissions for a user.

- Reports need optimising. Focus on stock related for now.
	- Dhiren asked for views to be checked out: https://cosoft.slack.com/archives/C03DRCT5PNK/p1752141740352959




- Discount Reference was put back as it broke CP. Portal is using Code. Remove existing Code references and use Reference instead. Portal label can show Code, but underlying property can be Reference.

- Check PLU code to make sure never null. Menu publish had items with null PLU which caused a bug. Find it.

- Portal is showing archived subcounts in stocktakes.

* JIRA
	- Remove Grv.Comments. We already have Notes which is in use.
	- https://cosoft.atlassian.net/browse/ACP-814 : Stock list frequency.
	- https://cosoft.atlassian.net/browse/ACP-795 : Change filter behaviour.
	- https://cosoft.atlassian.net/browse/ACP-810 : Currency stuff
	- https://cosoft.atlassian.net/browse/ACP-812 : Change password screen		
	- Wherever we are archiving records, remove unique constraints on Name, and use the audit log to log who archived the record.
	- Only allow posting a stock take if there are items.
	- Only allow posting a GRV or Return if there are items.
	- Only use Decimal(12,6) (default, alter as needed), not float etc... StockTakeItemSubCount BulkCounted and PreppedCounted, and related models.
	
API ISSUES: https://cosoft.atlassian.net/jira/software/c/projects/API/issues

- Store payment methods: When enabling a method that requires config, an internal server error is shown instead of a message indicating what config is required.
- Store payment methods: If you enable a method with config, you lose the config when disabling and re-enabling. Check if there is config when disabling, and if any - don't delete.
- Simplify the listing of permissions.
- Manufactured stock: Factor in stock count.
- Manufactured stock: Factor in costs.
	- Cost per unit produced in the specno screen should rather go next to the stock item selector. 
	- Costs are not needed for apportioning.
- Apportioned stock: Factor in waste. Chat with Leigh.

- Romans requires the following	
	- Optional items will require menu update.
	- Stock take order packs.
		- https://cosoft.atlassian.net/browse/ACP-790
			

- Screens that need archive and/or restore functionality.
	- Suppliers. Can archive. Need restore.
	- Stock lists: Can archive. Need restore.

* GRVs: Pd from shift selection: Update doc. 	- https://cosoft.atlassian.net/browse/ACP-525
* GRVs: Prevent adding items until a supplier selected: https://cosoft.atlassian.net/browse/ACP-718
* Sean asked that we show the device name in the payments screen for VirtualDeviceId. The Id does not mean anything to them.

- Reports page: Menu Item Recipes: Fix component spacing. Let the actual components determine width, so the container can auto size.
- Portal frequently displays a JS error in the console trying to dotnet ref a combobox or something.
- Portal maintenance page is not displaying correctly. We get a mess of cached stuff just garbled all over. Index.html must not be cached - ever. Then perhaps the maintenace page will display.
	- What about a different name for the maintenance page so not the same as index.html? Must just remove it once deployed.
- If the Portal is open, and a deployment is happening - and the portal tries to access a script - like isDevice - we get a break in the Portal.
	- Portal should be able to operate while updating. Perhaps deploy scripts and the list FIRST so they are quickly available?

- There is a Telerik licensing issue in the build process.
	/root/.nuget/packages/telerik.licensing/1.4.6/build/Telerik.Licensing.targets(4,3): Telerik and Kendo UI Licensing warning TKL002: No Telerik and Kendo UI License file found. [/opt/atlassian/pipelines/agent/build/Libraries/Aura.Portal.Components/Aura.Portal.Components.csproj]
	/root/.nuget/packages/telerik.licensing/1.4.6/build/Telerik.Licensing.targets(4,3): Telerik and Kendo UI Licensing warning TKL002: The following locations were searched: [/opt/atlassian/pipelines/agent/build/Libraries/Aura.Portal.Components/Aura.Portal.Components.csproj]
	/root/.nuget/packages/telerik.licensing/1.4.6/build/Telerik.Licensing.targets(4,3): Telerik and Kendo UI Licensing warning TKL002:  * TELERIK_LICENSE (EnvironmentVariable) [/opt/atlassian/pipelines/agent/build/Libraries/Aura.Portal.Components/Aura.Portal.Components.csproj]
	/root/.nuget/packages/telerik.licensing/1.4.6/build/Telerik.Licensing.targets(4,3): Telerik and Kendo UI Licensing warning TKL002:  * KENDO_UI_LICENSE (EnvironmentVariable) [/opt/atlassian/pipelines/agent/build/Libraries/Aura.Portal.Components/Aura.Portal.Components.csproj]


- Global permissions error. Showing "Unable to list global roles" for a new Brand Owner with only Neils Pizza company selectd (No brand or store)

* When Portal is deploying, we are getting a big X on the screen (check Franks screeny: https://files.slack.com/files-pri/T03TFVA9J-F08R4JVBV3M/screenshot_2025-05-06_at_08.25.00.png)	 

* Prevent duplicate stock takes up to the same minute. If any exist, then return it rather.

* Users: The Roles modal is not showing roles correctly it seems.
* Roles and permissions: Modal: Update the POS tab to reflect the current theme.



* Stock items: Form tab UI needs updating. Portal tab done.

* Login screen does not show errors.
	- Validation also looks ugly.

* Look into an MCP server for our API. Perhaps one per Microservice?

* BUG: Globals break. https://cosoft.atlassian.net/browse/ACP-765
	- After seaching for a company, then select it. Click on brand dropdown, company goes blank then cannot be set.


* If LoggedInUser is NOT Cosoft.	
	- All filters limited to the selected Brand or Store.
	- Editing a user. Use the user brand/store in the request so it is maintained. Currently using Globals, but we want to ignore them.

* BUG: Role assignment: for Mike Bowner under Mikealot
		- Roles per brand tab should be showing the selected brand. It is available in the user editor!

* Configure a user for global access and see if they get all brands and stores.
	- This will be great for support users. Only Cosoft can have global access.

* Sort out permissions needed for stock and menu. They need to be available to Store Owner stakeholders.	
	- Users must be Brand Owner/User to get access to Brand level permission.
		- Currently Salt are Store Owner. They will need to be upgraded to Brand Owner. Ensure when changing the stakeholder type, permissions already assigned are adjusted.
	- Some stock and menu permissions should only be managed by Brand Owner/User stakeholders. Then pages like Stock Items should be viewable to Store level users but only their store section editable.		
	- Stock items: If loggedInUser is a Store Owner/User, then they should not be able to edit or create stock items. Only modify the store related sections.		

* Testing of permissions
	- Have to be able to login as Store Owner, and admin the menu at the brand level. 
		- Store User will need to be given access to the Brand.		

* Stock lists: https://cosoft.atlassian.net/browse/ACP-763. UI update.

* The globals event handlers should put all code in the GlobalsManager class. Better design.

* Updating Stock Items to bring in line with Stock Takes UI.
	- https://cosoft.atlassian.net/browse/ACP-759


* Leigh: Mike do we have to do a call for every line item of the GRV or is there an endpoint to just pass in the list of items in one call?
	- {{gatewayUrl}}/brands/{{brandId}}/stores/{{storeId}}/grvs/{{grvId}}/items
	- Update this to accept an array of ids.		
* Going to open up stock and menu to general use in the next week or so. Must make this work via permissions now. Currently hard coded to hide menu items.


* Share Postman stuff.
* MCP browser_tools. See how we can use this with Blazor debugging.
* Consolidate AI's subscriptions.
   - No longer need Claude personal as we have Teams.
   - No longer need Github Copilot. Disable entirely everywhere. It's crap.
   - Windsurf we may be able to can. Cursor just got an update today so it may be better now. Compare and action.						

	- In GlobalsManager, we currently depend on the events to fire to know when changes happen and stuff. Rather remove the event handling, and handle it all in the appropriate Set handlers.
	- If PageRequirement is BrandOrStore, then Store should not be disabled if only 1 item. The user needs to be able to deselect the store. This came up in Stock items as you cannot deselect the store if only 1.
		- https://cosoft.atlassian.net/browse/ACP-737
	- BUG: Select Alphapos / Mikes coffee house which has no stores. An error is shown and the previous stores remain for selection. Should be cleared.

		
	- Bug on Prod reported by JP: https://cosoft.atlassian.net/browse/ACP-735

	- MenuRevisionActivation and MenuRevisionActivationSummary are not equal. Portal must be updated to match backend.

	- Stock stuff								
		- GRV: When posting a GRV, make sure taxes align and all balances before posting on the backend.
	subcounts is empty at first and then fills up with the subcount labels only after a few seconds.	
		- Green border around active brand or store. --palette-03: 5D9B00
		- GRV's page to TelerikForm. Layout has gone wonky.
			- Check stock takes too.

	- BUG: Listing Pos users for store Mikelado results in an error. Only this store though. Check it when the local DB is a Test DB again.

	- Does it happen with other CoGridForm implementations? (Cannot remember the context of this)
		- Stock takes: Yes.			
		- Stock lists: No.
		- Where the fix is done in CoGridForm, could be the ideal place to check for changes too and prompt.

	- Test stock stuff on Prod.

	- Test users page. Old pages are gone after this.
		- Able to configure brand users.
				
	- JIRA tasks. Mostly permissions now.
		
	- Use cases for the Users page.
		- Cosoft admin
			- Should be able to view all users in the system and no limitations by globals.
			- Should be able to give a user access to any brand or store.
			- Should be able to assign agents to roles and permissions (Sean does this a lot)
		- Admin
			- Should be able to give the user access to a brand if the user a brand stakeholder.			
				- Sean added a new user 'msemoli@cosoft.co.za' as Cosoft stakeholder and role helpdesk specialist. Does not have access to everything though cos we don't have a UI to allow roles to see all.

	- Deploying on Mon 17 Mar. Cosoft admins must have full access to users as the old methods are dead.

	- Prod DB testing.

	- Legal entities showing when they should not for a store user.	
	
	- Clean up tasks in the My Work link: https://cosoft.atlassian.net/jira/your-work	
				

	* Re-work the GRV/Returns screen with TelerikGridLayout.
	* Users screen. Long save times.

	* JIRA tickets.
	* When accessing the Portal not logged in, the following message displays like 20 times - and not even logged in.
		- Cannot init menu as the logged in user is null.
		- Pretty much just check all the initial loading of stuff before login (in the console).	
			
	* Permission features and bugs.
		- Brand level permission for JP.

	* Update ReceiptTypes to match backend once merged. Seems like the TJ stuff not in use in the Portal though.


* Grid based "add new" component. Need to figure out best way.
* Data dirty checker - global one.
* Keyboard handling for GRV.
* GRV paid from shift needs a way to reference shifts that have closed (like when viewing an older GRV)

* Reports UI is fucked after card CSS updates.
* https://cosoft.atlassian.net/wiki/spaces/DT/pages/749043714/Stock+Take+Enhancement
* Stock take
	* Form changes.
		* Show filters and stock take properties on their own lines. 
			* Filters panel: Filters: <show filters>.
			* Stock take panel: Stock levels for Date and time.
		* Show posted or draft status, but no dot or name.
		* Draft and Posted must show jogs. UI does not show for Draft.						

* Stock list and suppliers.
	* BUG: Select a stock list, change its name and click save. It becomes a new stocklist.		
	* Is dirty. Will include with stock takes.
	* Pagination. Can add with stock takes.
	* Better async when selecting/deselecting multiple stock items.

# Permissions.
	* Cosoft users must never have POS access. Perhaps even a permission implemented to prevent creating an employee - only view for support.
	* Roles
		* Add Cosole Role when on the Cosoft stakeholder.
		* Form should also show new Cosoft role.
		* Hide POS Permissions if a Cosoft user.
		* Change globals to All blah for Cosoft stakeholders.
	* Cosoft users won't require a brand or store in the users page.

* Bug
	* When searching, the form view must change to new, and go back to the grid view.		


* JWT (Pushing this out until stock is done. Pick auditing out of it)
	* Get merge conflicts sorted. Then cherry pick out features and deploy iteratively while we work on stock.
		* Change auditing - applied to stores currently.
		* Permissions HasFullAccess config. This will be needed when the updated permissions list is ready.
		* Remove permissions from the token and include them in the session.
		* Remove authenticated user.

# Stock					
	* Stock lists frequency when Janke has an update.			
		
* Close some tickets.			

	* Loading is hitting the API 3 times in stock lists OnParametersSetAsync.
		
	* Stock takes
		* Permission needed to edit a read only stock item in a stock take take.
		* When the report is executed for a stock take that is not finished, stock items must be made read only and a user requires permission to edit further.
		* Can edit items that are added after the report ran.	

# Finish JWT merge. Maybe start testing if time.
* Online ordering must ensure it only works on the brand it is allowed to.	

* Test	
	* In-store service and payments.
	* Portal and device login. 
		* How is UserId handled in the middleware after login. Do the correct headers get set.
	
	* Device registration, activation and status query.
	* Device Ping.
	
	* TransactionManager.CreatePaymentTransactionAsync.	
	
	* BrandId needs to go into the session for OO when creating. Check old code for claims.
	* Look at storing IntegrationPartnerLoginMapId in the Session for OO sessions. Enabled brand ids too.

* BaseCrudManager : This is using authToken all over. Get rid of it.
	* Search //??? through the code and fix up. Waiting for further attention once the dust settles.
	* WebApiClient
		* DeleteAsync has to keep authToken for now. All usages have been removed except for PaymentManager.PerformPaymentCancellationAsync.
			This method uses authToken in DeleteAsync to pass the stores api key.
			Might be a good idea to copy and only pass the SessionId around in the token instead of a full token?

	* Test Online Ordering and apply whatever fixes are needed there.
	* Aura.Service.InStore.Api.AuthController needs testing/updating.

	* DeviceStoreMap.LinkedByLoginId : Change to User.
	* ConsolidatedMenuRevisionActivation.CreatedByUserId was being set by LoginId. It is fixed now, but check that the backing field is indeed UserId.
	* Roles CRUD needs testing. Lots to do with authenticated user id in here.
		* RoleSetArgs
	* Check everything using IAuditableEntity.
	* BaseEntityService.CreateAsync configures audit tables. Test and figure out a better way if possible.
	* Make sure MyProfile works. 
	* RefundTransaction.LoginId. Refactor to UserId.
	* DeviceManager.AuthenticateDeviceAsync : Check this. Handles logins and stuff.
	* PaymentTransaction.LoginName can change to UserId. This is the DeviceId actually.

	* LoginsService must die.
	* Cleaning up test data in test.
	* Auditing.
	* Companies modal looks ugly. Should max width.
	* New company and brand updates. 
	* We need permissions for the menu, so if a company is selected and a Cosoft user, basic permissions are auto allocated. Need a better way of creating a company.
	
	* Something is making use of AuthenticatedUserClaims somewhere. Cannot remember where. Find it.
					

	* Look for //??? in the code and fix.
		* RecipeRevision needs to be updated from LoginId to UserId.
		
	* IntegrationPartnersController
	* Brand.BrandImagesController has 2 commented out places for args.AuthToken = AuthToken. Make sure this still works.
	* PostAsync.
		* OnlineOrdering.IntegrationPartnerManager.CreateLoginForIntegrationPartnerAsync is doing a login. I have removed the authenticatedUser that was posted with it. Should not matter, but check anyway.
			* AddBrandToIntegrationPartnerLoginAsync too.
		* ZatcaOnboarding.AuthenticateAsync()
			* This sets a global authToken variable, and it used in subsequent api calls. This should just be sessionId.
		* OnlineOrderingController.CreateOrder()
			* Removed authToken. Make sure it still works.
		* OnlineOrderingManager.CreateSessionAsync()
			* Needs authtoken it seems. Dig in.	

* JWT
	* NOTES
		* Dan is not making use of LoginId or LoginName, so this is purely internal now (unless a 3rd party uses it).
		* LoginName is only used for DeviceId (GUID) in the system. Not needed otherwise.

	* Portal Updates.
		* LoginPermissionSet.LoginId to .UserId.
	* Removed AuthenticatedUser.LoginPermissions
		* Test : StoreManager.ListStoresAsync. This has a check for the OnlineOrdering permissions and if not present, checks for allowed stores.
		* Test : DeviceManager.RequestNewAuthenticationCodeAsync
		* Test : MediatorManager.HandleListStoresRequestAsync. 
			* Lots of code in here got adjusted. Look everywhere that uses AuthenticatedUser.

	* The following should be removed/relace/updated.
		* TokenGenerator.GenerateToken			

* Setting printer config on tills is not persisting. Leigh is removing items and when tabbing away and coming back, they are there again. Possibly an error being swallowed.
	* Dhiren looked up the errors and saw Site Id was not being set for the till. It should surface on the Portal side.
	* Leigh's store: 61334


* Font on the navigation menu is odd (check Franks message). Frank showed the mobile version, but should be broken same on desktop.
* When scanning in a password for a POS user, ignore CRLF that comes with it if any.
* https://cosoft.atlassian.net/browse/ACP-287: Cannot activate mobile pos device.
* FlushDB on Brand startup.
* Brand owners not working 100%. JP was trying to configure brand owners and roles were not working. Check the chat.

* hotfix/user-permission-management : Check this has been merged on master.
* Delete Store for Neil. Store Id - NP4,  in company Neils pizza 2

* Clicking on Role permissions shows a progress indicator. Make this how all grid buttons work in Users too.
* Adding and removing roles shows the global progress indicator, and one in the grid. Does not look lekker.


* User role assignment
	* Remove the progress indicator in the grids after setting/unsetting. This won't apply if the task below is done.
	* Each tick in a checkbox is an API call and doc dump. Introduce Cancel/Submit and it it once only.	

* Do stores get updates when a user is removed from a role? The store needs to know they are no longer assigned.
	* I think for now we are only dumping directly assigned. Must make provision for this.

* If a user has a company, but no brand - the Portal shows an error when selecting the company. Perhaps make this silent.
* If a user has a company and brand, but no store - the Portal refuses to login if that brand is selected in the bootstrapper. Test was "A new company" which made it appear first.

* Ensure passwords unique when assigning a user to a POS role.

* Speed up document sync when saving an employee. Doing 4 docs currently.
* Lookup to make sure password not in use.	
* Mandatory map integration columns when setting charge rates.
	* https://cosoft.atlassian.net/browse/ACP-266

* Query to make sure a user has a unique password when assigning to a store.
	* Need to properly figure out this multi store/password thing.
* Can press ESC to close the users modal without the Abandon prompt. Move prompt to whatever is closing except save.
* Managing users as a non Cosoft user.
	* Setting Portal access without POS access will make it hard to find the user until they have roles assigned that point to the store.
	* When selecting a brand, should show users that can see the brand via their store. Currently it's direct brand access only.
	* Disable changing the stakeholder type if any roles are assigned.
* Role assignment: When all roles are unticked, permission set should reflect that. (Is this perhaps permission to role assignment)?
* Role assignment: Should we change this to a Submit type dialog too and only save on submit? Currently per tick.
	* Should load first then display, like Roles / Role-Permissions.
	* Only save and refresh grid on Submit.	
* Task for Dan to change from EmpNum to PosUserId.	
* Check out the KDS and ONS screens in Figma for design changes. Don't do anything * just look.
* Stores
	* Clicking the modal button should show a loading indicator.
* Kitchen Display Screens.
* If no store selected, say so.
* When digging around the Stores page, I got the grid showing a loading indicator as well as the Site loading indicator			
* Portal: Language switching?
	* Look into ways of handling this.	
* configuration/pos-setup/kitchen-display-screens?gp=Vbs8rhJz5
* Name is not showing if many columns. Name should have a min-width assigned.					
* The blue status we have in the pages when something needs to be selected has a design in Figma. Find it, and set it.
* When assigning roles/brands/stores to a user, the group checkbox is not updating in real time. Requires a refresh of the data to update which should not be necessary.
* Should a user be able to see the POS password if not set?
* If a user has POS access configured (Id > 0), validation checks should be in place for Nickname and Employee *.
* Users: If brand or store selected, get a list of UserIds that can see the brand/store via their roles and include in the query. Limit by allowed stakeholder. 
* This is done. Test it: Make sure you can configure Portal and POS access with new setup.
	* Remove User.IsEnabled and update to enable specific platform access/denial.
	* Cosoft user should be able to configure POS access without a store selected. Can look the user up and link via roles.
* UI updates coming for Store config. Already migrated to a Telerik tabstrip on Fri so partly done.
* Brief Portal run through to check other pages as the Basepage has been updated to accommodate latest layout.
* Check pages and globals work as intended.
	* Check grids to ensure they look and work as intended.
* MapManyRolesToBrandOrStoreAsync : Permission check is broken.				
* New endpoints to get data for Per Brand and Per Store. Leave the existing one in case we put it back one day.
* Initially, we may change an employee but not permissions. Dump both the brand permissions and the store employees same time to ensure they are in sync. Anytime a role, permission or user changes.
* When changing a brands currency symbol, the brand_18_store_61334_StoreSettings doc is only updated when updating a store.
* Finish off layout stuff in the Users modals.
	* Look for not done yet on desktop.
	* Mobile layout.
	* User Details icon should change between an eye or pencil depending on permissions. Can Manage/View Logins.		

*Test
	* Doc dump.
	* When checking/unchecking the group checkboxes for users/roles, it takes a while to update. Probably StateHasChanged?
	* Users: Details: Bug when setting a Portal user from the modal. Not showing the created password.
	* Enable showing the password.
	* Also send an email with the users password.			
* Leigh does not want tax rates in Store. Should be company/country.


*JWT branch:
	* Currently all permissions are permission set Admin. Need to update this so the most basic permissions for logging in, managing own store, and viewing reports is easy to assign.
	* https://docs.telerik.com/blazor-ui/styling-and-themes/figma-ui-kits
	* Final test: Keep going through msmit@cosoft and miketest@cosoft tests. Miketest must be able to setup employees and all exist in the doc.
* When setting Portal Permissions for a role * don't dump docs. Only do a doc for POS permission assignment.
* Use Stakeholder for filtering users. Only a Cosoft stakeholder can list without filters or something.
* Bugs.
	* Listing of users is returning users with Employee Number = DCS.
	* When setting a POS users password, check if in use rather than letting the DB fail on duplicates.
* JWT.
	* Clean up permission names.
	* Authenticated user to user id.
	* Internal endpoint calls.
	* Logging out set expiry date to now.
	* Move device and OO logins out of PortalUsers into their own tables. Work something out.
	* Deauth a device, remove permission for it.
	* Portal permissions.
	
	* Stakeholder we put on hold. Any further thought gone into this.
* At some point...
* Check out the errors popping up at portaltest.aurapos.com (S3 bucket).
* Check out https://github.com/Giorgi/EntityFramework.Exceptions for better DB exception handling.
* ResetPassword is loading up the bootstrapper. Should not. Login too * bootstrapper must not execute for the login page to load. Check.
* Chat with Frank about using GIT. Setup a script for him to pull and push.
* Need a script to backup Test, and restore Local * with just 1 execution. Can backup local nightly then and stuff like that.
* Bunch of console integrity errors on Test. Try get that cleaned up.
* PWA not working on test/prod.