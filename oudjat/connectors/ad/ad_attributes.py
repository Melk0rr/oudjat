attributes = {
  "user": [
    "accountExpires",
    "cn",
    "description",
    "employeeID",
    "givenName",
    "lastLogon",
    "mail",
    "objectSid",
    "pwdLastSet",
    "sn",
    "sAMAccountName",
    "title",
    "userAccountControl",
    "whenChanged",
    "whenCreated"
  ],
  "computer": [
    "description"
  ]
}

def get_ad_attributes(ad_type: str = "user"):
  """ Helper function to return AD attributes based on type """
  return attributes[ad_type]