from enum import Enum

class LDAPSearchTypes(Enum):
  DEFAULT = {
    "attributes": [
      "distinguishedName",
      "name",
      "gpLink",
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
      "gpLink",
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

  PERSON = {
    "filter": "(&(objectClass=person)(!(objectClass=computer)))",
    "attributes": [
      "accountExpires",
      "cn",
      "description",
      "distinguishedName",
      "employeeID",
      "givenName",
      "gpLink",
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

  COMPUTER = {
    "filter": "(objectClass=computer)",
    "attributes": [
      "cn",
      "description",
      "distinguishedName",
      "gpLink",
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
  
  GPO = {
    "filter": "(objectClass=groupPolicyContainer)",
    "attributes": [
      "displayName",
      "gPCFileSysPath",
      "gPCUserExtensionNames",
      "gPCMachineExtensionNames",
      "name",
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
      "gpLink",
      "member",
      "memberOf",
      "objectSid"
    ]
  }

  OU = {
    "filter": "(objectClass=organizationalUnit)",
    "attributes": [
      "description",
      "gpLink"
    ]
  }