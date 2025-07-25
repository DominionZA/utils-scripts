SET foreign_key_checks = 0;


USE aura_cloud_invoicing;

CREATE TABLE IF NOT EXISTS aura_cloud_device.PingHistory (
  Id bigint UNSIGNED NOT NULL AUTO_INCREMENT,
  DeviceId int NOT NULL,
  Time datetime NOT NULL,
  PRIMARY KEY (Id)
)
ENGINE = INNODB,
CHARACTER SET utf8mb4,
COLLATE utf8mb4_0900_ai_ci;

truncate TABLE aura_cloud_device.PingHistory;
truncate TABLE aura_cloud_device.DeviceVersionHistory;

truncate table InvoiceTotalTaxation;

truncate TABLE KitchenStepBasketSetLineItem;
truncate TABLE KitchenStepBasketSet;
truncate TABLE KitchenStep;

truncate table LineItemTaxation;
truncate table LineItem;
truncate table BasketItemTaxation;
truncate table BasketItem;
truncate table Payment;
truncate table InvoiceDiscount;
truncate table BasketItemGroupTaxation;
truncate table BasketItemGroup;
truncate table BasketSet;

truncate table aura_cloud_payment.RefundTransactionResponseData;
truncate table aura_cloud_payment.RefundTransactionReversal;
truncate table aura_cloud_payment.RefundTransaction;

truncate table CashupDataSalesRecordPayment;
truncate table CashupDataSalesRecord;
truncate table CashupDataVoidRecord;
truncate table CashupDataGratuityExpense;
truncate table CashupDataReconCashOnHand;
truncate table CashupDataPaymentControl;
truncate table CashupDataSalesChannelRecord;
truncate table CashupDataTillFloatExpense;

truncate table aura_cloud_online_ordering.MediatorRequest;
truncate table aura_cloud_online_ordering.OnlineOrder;

truncate table external_integration.DCS_InvoiceState;
TRUNCATE TABLE external_integration.DCS_NotificationLog;
truncate TABLE external_integration.DCS_Driver;
truncate TABLE external_integration.DCS_StoreMap;
truncate table external_integration.Deliveree_InvoiceState;
truncate TABLE external_integration.Deliveree_NotificationLog;
truncate table external_integration.Deliveree_Driver;
truncate TABLE external_integration.Deliveree_StoreMap;
truncate TABLE external_integration.MarketMan_InvoiceState;
truncate table external_integration.MarketMan_SalesPeriodContainer;
truncate TABLE external_integration.StoreIntegrationJobConfiguration;
truncate TABLE external_integration.StoreIntegrationJob;
truncate TABLE external_integration.BrandIntegrationJobConfiguration;
truncate TABLE external_integration.BrandIntegrationJob;
truncate TABLE external_integration.LatestTransactionActivity;
truncate TABLE external_integration.IntegrationPartnerConfigurationValue;
truncate table external_integration.IntegrationPartnerConfiguration;


truncate table Invoice;
truncate table InvoiceTotal;

truncate table ActiveEmployeeShift;
truncate table EmployeeShift;
truncate table ActiveEmployeeLogin;
truncate table EmployeeLogin;
truncate table EmployeeCashup;
truncate table TillCashup;
truncate table syncmanager.ShopCashupTracker;
truncate table ShopCashup;

truncate table CashupDataNote;
truncate table CashupDataEmployeeFloatIssuedExpense;
truncate table CashupDataEmployeeFloatReceivedExpense;
truncate table CashupDataPettyCashExpense;
truncate table CashupDataWageExpense;
truncate table CashupDataSalesPaymentMethodSalesChannel;
TRUNCATE table CashupDataSalesPaymentMethod;
truncate table CashupDataSalesChannelControl;
truncate table CashupDataGrvExpense;
truncate TABLE CashupDataFloatCarriedForward;


truncate table CashupData;

truncate table CouchDocument;

truncate table aura_cloud_payment.PaymentTransactionResponseData;
TRUNCATE TABLE aura_cloud_payment.PaymentTransactionStepInputField;


truncate table aura_cloud_payment.PaymentTransactionStep;

truncate table aura_cloud_payment.PaymentTransactionReversal;

TRUNCATE TABLE aura_cloud_payment.PaymentTransactionEvent;
truncate table aura_cloud_payment.PaymentTransactionBasketInfo;
truncate table aura_cloud_payment.PaymentTransaction;

truncate table aura_cloud_brand.AccessLog;
truncate TABLE BBSQLInvoiceLineItem;
truncate table BBSQLInvoice;

truncate TABLE aura_cloud_device.ActivationCode;

truncate TABLE aura_cloud_device.PingHistory;

truncate TABLE aura_cloud_device.DeviceStoreMap;
delete from aura_cloud_device.Device WHERE DeviceId <> 'CloudServer';

delete FROM aura_cloud_auth.PortalUser WHERE LoginName like '%-%-%-%-%';
truncate table CustomerAddress;
truncate table Customer;

truncate TABLE aura_cloud_payment.TillPaymentMethodConfigurationConfig;
truncate table aura_cloud_payment.TillPaymentMethodConfiguration;

truncate TABLE aura_cloud_payment.StorePaymentMethodProfileConfig;
truncate table aura_cloud_payment.StorePaymentMethodProfile;

truncate TABLE syncmanager.LastSequence;
truncate TABLE syncmanager.DocumentSequence;
truncate table syncmanager.DocumentVersion;

UPDATE aura_cloud_auth.PortalUser pu set pu.Password = '$2b$10$ny53I3Z91JE/waFKEGUZ4OYX5eNZGuwYxxxB4370TbnjnjYhWtpNi' WHERE pu.LoginName like '%dhiren%';

CREATE USER IF NOT EXISTS 'msmit'@'%' IDENTIFIED BY 'P@ssw0rd1';
CREATE USER IF NOT EXISTS 'admin'@'%' IDENTIFIED BY 'P@ssw0rd1';

SET foreign_key_checks = 1;

UPDATE aura_cloud_brand.VirtualDevice vd SET Name = 'TILL1' where Id = 710;
UPDATE aura_cloud_brand.Store SET IsNextGen = 1, TimeAndAttendanceVirtualDeviceTillId = 710 where Id = 'TEST01';
INSERT IGNORE INTO aura_cloud_brand.VirtualDevice (StoreId, Name, IsEnabled, DeviceTypeId) VALUES ('TEST01', 'Online Ordering', 1, 8);
set @tillid = LAST_INSERT_ID();
INSERT IGNORE INTO aura_cloud_auth.PosUser (StoreId, AbbreviatedName, EmployeeNumber, Password, IsEnabled, PosUserTypeId, PosPassword) VALUES ('TEST01', 'ONLINE', 'ZZZ', UUID(), 1, 1, uuid());
set @employeeid = LAST_INSERT_ID();
INSERT IGNORE INTO aura_cloud_auth.User(Name, Surname, StakeholderId, PosUserId) VALUES ('ONLINE', 'ORDERING', 5, @employeeid);
INSERT IGNORE INTO aura_cloud_online_ordering.StoreProfile (Id, UseMediator, TillId, EmployeeId, StoreDesignatedVirtualDeviceId) VALUES ('TEST01', 0, @tillid, @employeeid, 710);
UPDATE aura_cloud_brand.Store s SET s.IsOnlineOrderingEnabled = 1 WHERE s.Id = 'TEST01';

INSERT INTO aura_cloud_brand.SalesChannel (Name, BrandId, HasAccount, IsForIntegrationPartner, IsEnabled, AlwaysUseAccount, `Order`) VALUES ('Cosoft Testing', 38, 1, 1, 1, 1, 1);
set @saleschannelid = LAST_INSERT_ID();
INSERT INTO aura_cloud_online_ordering. IntegrationPartnerLoginBrandMap (IntegrationPartnerLoginMapId, BrandId, IsEnabled, SalesChannelId, TimestampAdjustmentMinutes) VALUES (8, 38, 1, @saleschannelid, 0);

insert INTO aura_cloud_payment.BrandPaymentMethodMap (BrandId, PaymentMethodId, IsEnabled) VALUES (38, 10, 1);
insert INTO aura_cloud_payment.StorePaymentMethodProfile (StoreId, PaymentMethodId, IsEnabled, PaymentMethodDisplayName, IsVisibleToCustomer, AutoBalanceCashup) VALUES ('TEST01', 10, 1, 'Pay by Card', 1, 1);
set @storepaymentmethodprofileid = LAST_INSERT_ID();

insert into aura_cloud_payment.StorePaymentMethodProfileConfig (StorePaymentMethodProfileId, DataKey, DataValue) values (@storepaymentmethodprofileid, 'BasePath',	'http://66.8.29.52:20002/tjpos/v1');
insert into aura_cloud_payment.StorePaymentMethodProfileConfig (StorePaymentMethodProfileId, DataKey, DataValue) values (@storepaymentmethodprofileid, 'Chain',	'Test');
insert INTO aura_cloud_payment.StorePaymentMethodProfileConfig (StorePaymentMethodProfileId, DataKey, DataValue) VALUES (@storepaymentmethodprofileid, 'MerchantId',	'RESTSIM00000001');

insert INTO aura_cloud_payment.TillPaymentMethodConfiguration (StorePaymentMethodProfileId, VirtualDeviceId) VALUES (@storepaymentmethodprofileid, 710);
SET @tillpaymentmethodconfigurationid = LAST_INSERT_ID();
insert INTO aura_cloud_payment.TillPaymentMethodConfigurationConfig (TillPaymentMethodConfigurationId, DataKey, DataValue) VALUES (@tillpaymentmethodconfigurationid, 'TerminalId',	'57290078');


SET sql_notes = 0;
SET sql_warnings = 0;

-- Drop foreign key first, then index, then recreate both
ALTER TABLE aura_cloud_device.PingHistory DROP FOREIGN KEY FK_PingHistory_DeviceId;
ALTER TABLE aura_cloud_device.PingHistory DROP INDEX IDX_PingHistory;
ALTER TABLE aura_cloud_device.PingHistory ADD INDEX IDX_PingHistory (DeviceId, Time);
ALTER TABLE aura_cloud_device.PingHistory ADD CONSTRAINT FK_PingHistory_DeviceId FOREIGN KEY (DeviceId) REFERENCES aura_cloud_device.Device (Id);