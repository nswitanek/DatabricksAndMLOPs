import json
import logging
import os

import azure.functions as func

from .azdo import get_pipeline_id, execute_pipeline


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

    DEVOPS_ORG = os.environ.get("DEVOPS_ORG", "NotAssigned")
    DEVOPS_PROJECT = os.environ.get("DEVOPS_PROJECT", "NotAssigned")
    # TODO: Make this more dynamic, perhaps some sort of control table
    desired_release_name = os.environ.get("RELEASE_NAME", "NotAssigned")
    # TODO: Make this a key vault secret
    DEVOPS_PERSONAL_ACCESS_TOKEN = os.environ.get("DEVOPS_PERSONAL_ACCESS_TOKEN", "NotAssigned")

    logging.info(f"ORG:{DEVOPS_ORG}")
    logging.info(f"PROJ:{DEVOPS_PROJECT}")
    logging.info(f"PIPELINE:{desired_release_name}")
    logging.info(f"PAT:{len(DEVOPS_PERSONAL_ACCESS_TOKEN)}")
    
    # Event Topic Structure
    # [Null(0), subscription(1), <value>(2), rg(3), <value>(4), provider(5),
    # <value>(6), , workspaces(7), <workspaces-name> (8)]
    parsed_topic = str(event.topic).split('/') 
    logging.info(f"TOPIC:{parsed_topic}")
    event_data = event.get_json()
    logging.info(f"ED:{json.dumps(event_data)}")

    try:
        RESOURCE_GROUP=parsed_topic[4]
        logging.info(f"RG:{RESOURCE_GROUP}")
        WORKSPACE=parsed_topic[8]
        logging.info(f"WS:{WORKSPACE}")
    except IndexError as e:
        logging.info("Failed to get either the RG or Workspace")
        logging.info(json.dumps(parsed_topic))
        raise e
    
    MODEL_NAME = event_data.get("modelName", "NotAssigned")
    logging.info(f"MODEL:{MODEL_NAME}")

    MODEL_VERSION = event_data.get("modelVersion", "1")
    logging.info(f"V:{str(MODEL_VERSION)}")
    MODEL_BUILD_ID = event_data.get("modelTags", {}).get("BuildId", "UNK")
    logging.info(f"BUILD:{MODEL_BUILD_ID}")
    
    logging.info('Operating on model(version): {}({})'.format(MODEL_NAME, MODEL_VERSION))
    logging.info('Searching for a DevOps Release named: {}'.format(desired_release_name))

    pipeline_id, message = get_pipeline_id(
        desired_release_name,
        organization=DEVOPS_ORG,
        project=DEVOPS_PROJECT,
        personal_access_token=DEVOPS_PERSONAL_ACCESS_TOKEN
    )

    if pipeline_id == -1:
        logging.info('Failed to process model registration: %s', message)
        return -1
    
    logging.info('Succeeded in finding a DevOps Release named "{}" with Id of {}'.format(
        desired_release_name,
        pipeline_id
        )
    )

    output = execute_pipeline(
        pipeline_id,
        organization = DEVOPS_ORG, 
        project = DEVOPS_PROJECT, 
        personal_access_token = DEVOPS_PERSONAL_ACCESS_TOKEN,
        azdo_variables= {
            "MODEL_NAME":{"value":MODEL_NAME, "isSecret": False}
        }
    )

    logging.info("Output of DevOps Execution: {}".format( json.dumps(output)))
