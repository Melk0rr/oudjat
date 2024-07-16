import keyring
import getpass

def save_credentials(service: str, username: str, password: str) -> None:
  """ Saves the given credentials for the provided service """
  try:
    keyring.set_password(service, username, password)

  except keyring.errors.PasswordSetError as e:
    raise(f"Error while saving credentials for {service}:{username}\n{e}")

def get_credentials(service: str) -> keyring.credentials.SimpleCredential:
  """ Returns user credentials for given service """    
  try:
    cred = keyring.get_credential(service, "")

    if cred is None:
      print(f"\nNo stored credentials for {service}. Please enter your credentials:")
      
      # Ask user's credentials
      username = input("Username: ")
      password = getpass.getpass("Password: ")

      # Saving credentials
      save_credentials(service, username, password)
      cred = keyring.credentials.SimpleCredential(username, password)
      
  except keyring.errors.KeyringError as e:
    raise(f"\nAn error occured while retreiving user's credentials for {service}\n{e}")
  
  return cred

def del_credentials(service: str, username: str) -> None:
  """ Deletes saved credentials for given service and username """
  try:
    keyring.delete_password(service, username)
    
  except keyring.errors.PasswordDeleteError as e:
    raise(f"Error while deleting password for {service}:{username}\n{e}")