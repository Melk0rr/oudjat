from enum import Enum

class LDAPSearchTypes(Enum):
  user = {
    "filter": "(&(objectClass=user)(!(objectClass=computer)))",
    "attributes": [
      "accountExpires",
      "cn",
      "description",
      "distinguishedName",
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
    ]
  }

  person = {
    "filter": "(&(objectClass=person)(!(objectClass=computer)))",
    "attributes": [
      "accountExpires",
      "cn",
      "description",
      "distinguishedName",
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
    ]
  }

  computer = {
    "filter": "(objectClass=computer)",
    "attributes": [
      "cn",
      "description",
      "distinguishedName",
      "lastLogon",
      "objectSid",
      "operatingSystem",
      "operatingSystemVersion",
      "pwdLastSet",
      "userAccountControl",
      "whenChanged",
      "whenCreated"
    ]
  }
  
  gpo = {
    "filter": "(objectClass=groupPolicyContainer)",
    "attributes": [
      "displayName",
      "whenChanged",
      "whenCreated"
    ]
  }

  group = {
    "filter": "(objectClass=group)",
    "attributes": [
      "cn",
      "description",
      "member",
      "memberOf"
    ]
  }

  ou = {
    "filter": "(objectClass=organizationalUnit)",
    "attributes": [
      "description"
    ]
  }

  device = {
    "filter": "(objectClass=device)",
    "attributes": [
      "cn",
      "serialNumber"
    ]
  }