import json
import logging
import os

import azure.functions as func

from .azdo import execute_release, get_release_id


def main(event: func.EventGridEvent):
    result = json.dumps({
        'id': event.id,
        'data': event.get_json(),
        'topic': event.topic,
        'subject': event.subject,
        'event_type': event.event_type,
    })

    event_data = event.get_json()
    RESOURCE_GROUP="" #event.topic
    WORKSPACE=""
    MODEL_NAME = event_data["ModelName"]
    MODEL_VERSION = event_data["ModelVersion"]
    MODEL_BUILD_ID = event_data["ModelTags"]["BuildId"]

    logging.info('Python EventGrid trigger processed an event: %s', result)

    model_subject, model_version = event.subject.split(":", maxsplit=1)
    _, model_name = model_subject.split("/", maxsplit=1)

    logging.info('Operating on model(version): {}({})'.format(model_name, model_version))

    # TODO: Make this more dynamic, perhaps some sort of control table
    desired_release_name = os.environ.get("release_name")

    logging.info('Searching for a DevOps Release named: {}'.format(desired_release_name))

    release_id, message = get_release_id(desired_release_name)

    if release_id == -1:
        logging.info('Failed to process model registration: %s', message)
        return -1
    
    logging.info('Succeeded in finding a DevOps Release named "{}" with Id of {}'.format(
        desired_release_name,
        release_id
        )
    )

    output = execute_release(
        release_id,
        azdo_variables= {
            "model_name":{"value":model_name}
        }
    )

    logging.info("Output of DevOps Execution: {}".format( json.dumps(output)))
