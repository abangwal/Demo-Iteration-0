import json
import openai
from pydantic import BaseModel, Field
from typing import List

# Create clientkey
client = openai.OpenAI(
    base_url="https://api.together.xyz/v1",
    api_key="85e577a7bd21434e2d3f1ab2bd7a2750c6db5eb7ddf09cce131655911c93f622",
)


class SubTask(BaseModel):
    sub_task: str = Field(
        description="A sub-task name to be done to complete the given task."
    )
    sub_task_description: str = Field(
        description="Detailed description about the subtask"
    )


class ListOfSubTasks(BaseModel):
    sub_tasks: List[SubTask] = Field(
        description="List of subtask to be done to complete the given task at hand."
    )


class DynamicInput:
    def __init__(self) -> None:
        pass

    def get_sub_tasks(self, message):
        response = client.chat.completions.create(
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            messages=message,
            response_format={
                "type": "json_object",
                "schema": ListOfSubTasks.model_json_schema(),
            },
            frequency_penalty=0.6,
        )
        response = response.choices[0].message.content
        r = json.loads(response)
        sub_tasks = []
        sub_tasks_description = []

        for i in r["sub_tasks"]:
            sub_tasks.append(i["sub_task"])
            sub_tasks_description.append(i["sub_task_description"])

        return sub_tasks, sub_tasks_description, response

    def run(self, query):
        user_query = query
        data_dict = {user_query: {}}
        message = [
            {
                "role": "system",
                "content": "You are a helpful and experienced market analyst. Use your own intelligence to provide the subtasks for completing the TASK. Dont use any formatting, Answer in provided JSON schema",
            },
            {
                "role": "user",
                "content": f"Tell subtasks to complete the TASK : {user_query}",
            },
        ]

        sub_tasks, sub_task_descriptions, assistants = self.get_sub_tasks(message)

        for i in range(len(sub_tasks)):
            print("Running", i + 1, "/", len(sub_tasks))
            query = sub_task_descriptions[i]
            temp_msg = message.copy()
            temp_msg.append({"role": "assistant", "content": assistants})
            temp_msg.append(
                {
                    "role": "user",
                    "content": f"Now Tell me subtasks to complete the TASK : {query}",
                }
            )
            sts, stds, _ = self.get_sub_tasks(temp_msg)
            response = list(zip(sts, stds))
            data_dict[user_query][sub_tasks[i]] = response

        return data_dict
