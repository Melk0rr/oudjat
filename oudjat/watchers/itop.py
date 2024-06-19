""" iTop module used to generate iTop tickets """
import json
import sys
import requests

from typing import Dict

from oudjat.utils.dictionary_join import join_dictionary_items


def new_ticket(itop_user: str, itop_pwd: str, ticket_data: Dict) -> None:
  """ Create a new itop ticket """
  if len(ticket_data.keys()) != 5:
    print(f"Those keys must be provided: host, service, service_status, service_state_type\n")
    sys.exit()

  else:
    print(join_dictionary_items(ticket_data, "\n"))
    host = ticket_data["host"]
    service = ticket_data["service"]
    service_status = ticket_data["service_status"]
    service_state_type = ticket_data["service_state_type"]

  if (service_status != "OK") and (service_status != "UP") and (service_state_type == "HARD"):
    json_data = {
        "operation": "core/create",
        "class": ticket_data["class"],
        "fields": {
            "title": ticket_data["title"],
            "description": ticket_data["description"],
            "org_id": f"SELECT Organization AS O JOIN FunctionalCI AS CI ON CI.org_id = O.id WHERE CI.name={host}",
            "functionalcis_list": [
                {
                    "functionalci_id": f"SELECT FunctionalCI WHERE name={host}",
                    "impact_code": "manual",
                }
            ],
        },
        "comment": ticket_data["comment"],
        "output_fields": "id",
    }

    encoded_data = json.dumps(json_data)
    r = requests.post(
        f"{ticket_data['url']}/webservices/rest.php?version=1.0",
        verify=False,
        data={
            "auth_user": itop_user,
            "auth_pwd": itop_pwd,
            "json_data": encoded_data
        }
    )
    result = json.loads(r.text)

    if result['code'] == 0:
      print("Ticket created.\n")
    else:
      print(f"{result['message']}\n")

  else:
    print("Service state type !='HARD', doing nothing.\n")
