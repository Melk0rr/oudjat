from enum import Enum

class LDAPObjectType(Enum):
  """ These are the default LDAP search parameters per object type """
  DEFAULT = {
    "objectClass": "*",
    "filter": "(objectClass=*)",
    "attributes": "*"
  }

  COMPUTER = {
    "objectClass": "computer",
    "filter": "(objectClass=computer)",
    "attributes": [
      "cn",
      "description",
      "distinguishedName",
      "lastLogonTimestamp",
      "msDS-User-Account-Control-Computed",
      "name",
      "objectClass",
      "objectGUID",
      "objectSid",
      "operatingSystem",
      "operatingSystemVersion",
      "pwdLastSet",
      "sAMAccountName",
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
      "name",
      "objectClass",
      "objectGUID",
      "objectSid",
      "whenChanged",
      "whenCreated",
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
      "objectSid",
      "whenChanged",
      "whenCreated",
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
      "lastLogonTimestamp",
      "mail",
      "name",
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

  SUBNET = {
    "objectClass": "subnet",
    "filter": "(objectClass=subnet)",
    "attributes": [
      "cn",
      "description",
      "distinguishedName",
      "location",
      "name",
      "objectGUID",
      "whenChanged",
      "whenCreated"
    ]
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
      "lastLogonTimestamp",
      "mail",
      "msDS-User-Account-Control-Computed",
      "name",
      "objectClass",
      "objectGUID",
      "objectSid",
      "pwdLastSet",
      "sn",
      "sAMAccountName",
      "title",
      "userAccountControl",
      "userPrincipalName",
      "whenChanged",
      "whenCreated"
    ]
  }