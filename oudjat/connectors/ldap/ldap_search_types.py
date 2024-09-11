from enum import Enum

class LDAPSearchTypes(Enum):
  DEFAULT = {
    "attributes": [
      "distinguishedName",
      "name",
      "objectClass",
      "objectGUID"
    ]
  }

  USER = {
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
      "objectClass",
      "objectGUID",
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

  PERSON = {
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
      "objectClass",
      "objectGUID",
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

  COMPUTER = {
    "filter": "(objectClass=computer)",
    "attributes": [
      "cn",
      "description",
      "distinguishedName",
      "lastLogon",
      "objectClass",
      "objectGUID",
      "objectSid",
      "operatingSystem",
      "operatingSystemVersion",
      "pwdLastSet",
      "userAccountControl",
      "whenChanged",
      "whenCreated"
    ]
  }
  
  GPO = {
    "filter": "(objectClass=groupPolicyContainer)",
    "attributes": [
      "displayName",
      "gPCFileSysPath",
      "gPCUserExtensionNames",
      "gPCMachineExtensionNames",
      "gPCWQLFilter",
      "name",
      "objectClass",
      "objectGUID",
      "versionNumber",
      "whenChanged",
      "whenCreated",
    ]
  }

  GROUP = {
    "filter": "(objectClass=group)",
    "attributes": [
      "cn",
      "description",
      "groupType",
      "member",
      "memberOf",
      "objectClass",
      "objectGUID",
      "objectSid"
    ]
  }

  OU = {
    "filter": "(objectClass=organizationalUnit)",
    "attributes": [
      "description",
      "gpLink",
      "name",
      "objectClass",
      "objectGUID",
      "whenChanged",
      "whenCreated",
    ]
  }