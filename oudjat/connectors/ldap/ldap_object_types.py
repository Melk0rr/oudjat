from enum import Enum

class LDAPObjectType(Enum):
  """ These are the default LDAP search parameters per object type """
  DEFAULT = {
    "filter": "*",
    "attributes": "*"
  }

  USER = {
    "objectClass": "user",
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
    "objectClass": "person",
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
    "objectClass": "computer",
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
    "objectClass": "groupPolicyContainer",
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
    "objectClass": "group",
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
    "objectClass": "organizationalUnit",
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