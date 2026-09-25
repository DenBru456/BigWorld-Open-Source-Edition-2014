BILLING_SYSTEM = ""

if BILLING_SYSTEM == "twisted_restful":
	from twisted_restful_billing import BillingSystem as connectToBillingSystem

elif BILLING_SYSTEM == "restful":
	from restful_billing import BillingSystem as connectToBillingSystem

elif BILLING_SYSTEM == "sqlite":
	from sqlite_billing import BillingSystem as connectToBillingSystem

else:
	def connectToBillingSystem():
		return None


def onInit( isReload ):
	print "FantasyDemo.onInit:", isReload

# FantasyDemo.py
