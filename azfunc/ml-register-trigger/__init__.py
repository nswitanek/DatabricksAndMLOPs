import json
import logging
import os

import azure.functions as func

import azdo


def main(event: func.EventGridEvent):
    # Expecting the following environment variables
    # RELEASE_NAME
    # DEVOPS_ORG
    # DEVOPS_PROJECT
    result = json.dumps({
        'id': event.id,
        'data': event.get_json(),
        'topic': event.topic,
        'subject': event.subject,
        'event_type': event.event_type,
    })
    logging.info('Python EventGrid trigger processed an event: %s', result)

    DEVOPS_ORG = os.environ.get("DEVOPS_ORG")
    DEVOPS_PROJECT = os.environ.get("DEVOPS_PROJECT")
    # TODO: Make this more dynamic, perhaps some sort of control table
    desired_release_name = os.environ.get("RELEASE_NAME")
    # TODO: Make this a key vault secret
    DEVOPS_PERSONAL_ACCESS_TOKEN = os.environ.get("DEVOPS_PERSONAL_ACCESS_TOKEN")
    
    # Event Topic Structure
    # [Null(0), subscription(1), <value>(2), rg(3), <value>(4), provider(5),
    # <value>(6), Msft.MLSvc(7), workspaces(9), <workspaces-name> (10)]
    parsed_topic = event.topic.split('/') 
    event_data = event.get_json()

    RESOURCE_GROUP=parsed_topic[4]
    WORKSPACE=parsed_topic[9]
    MODEL_NAME = event_data["ModelName"]
    MODEL_VERSION = event_data["ModelVersion"]
    MODEL_BUILD_ID = event_data["ModelTags"]["BuildId"]
    
    logging.info('Operating on model(version): {}({})'.format(MODEL_NAME, MODEL_VERSION))
    logging.info('Searching for a DevOps Release named: {}'.format(desired_release_name))

    release_id, message = azdo.get_release_id(
        desired_release_name,
        organization=DEVOPS_ORG,
        project=DEVOPS_PROJECT,
        personal_access_token=DEVOPS_PERSONAL_ACCESS_TOKEN
    )

    if release_id == -1:
        logging.info('Failed to process model registration: %s', message)
        return -1
    
    logging.info('Succeeded in finding a DevOps Release named "{}" with Id of {}'.format(
        desired_release_name,
        release_id
        )
    )

    output = azdo.execute_release(
        release_id,
        organization = DEVOPS_ORG, 
        project = DEVOPS_PROJECT, 
        personal_access_token = DEVOPS_PERSONAL_ACCESS_TOKEN,
        azdo_variables= {
            "model_name":{"value":MODEL_NAME}
        }
    )

    logging.info("Output of DevOps Execution: {}".format( json.dumps(output)))
