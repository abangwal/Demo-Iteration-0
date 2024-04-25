import json
import openai
from schemas import LoS, SWOTAnalysis

client = openai.OpenAI(
    base_url="https://api.together.xyz/v1",
    api_key="",
)


class CompetitorAnalyst:
    def __init__(self, industry):
        self.industry = industry

    def get_message(self, task, **kwargs):
        if task == "web-query":
            message = [
                {
                    "role": "system",
                    "content": "You are a helpful assistant. Use your intelligence to complete the task.",
                },
                {
                    "role": "user",
                    "content": f"Web search queries for DuckDuckGo search engine for '{kwargs['query']}'",
                },
            ]
        elif task == "competitors-name":
            message = [
                {
                    "role": "system",
                    "content": "You are a helpful and experienced market analyst. Use your intelligence and the provided context(if needed) to complete the task.",
                },
                {
                    "role": "user",
                    "content": f"Name that competitors in the '{kwargs['industry']}' industry.\n\nCONTEXT :\n {kwargs['context']}",
                },
            ]
        elif task == "swot-analysis":
            message = [
                {
                    "role": "system",
                    "content": "You are a helpful and experienced market analyst. Use your intelligence the provided context(if needed) to complete the task.",
                },
                {
                    "role": "user",
                    "content": f"SWOT analysis on {kwargs['competitor_name']} as a business.\n\nCONTEXT :\n{kwargs['context']}",
                },
            ]
        else:
            message = [None, None]
        return message

    def get_response(self, response_schema, message, repetetion_penalty):
        response = client.chat.completions.create(
            model="mistralai/Mistral-7B-Instruct-v0.1",
            messages=message,
            response_format={
                "type": "json_object",
                "schema": response_schema.model_json_schema(),
            },
            frequency_penalty=repetetion_penalty,
        )
        content = json.loads(response.choices[0].message.content)
        return content

    def do_analysis(self):
        industry = self.industry

        # get competitors name
        message = self.get_message(
            task="competitors-name", industry=industry, context=""
        )
        competitors_names = self.get_response(
            response_schema=LoS, message=message, repetetion_penalty=0.5
        )["los"]
        final_report = {}

        # do SWOT analysis for each competitor
        for competitor in competitors_names[:4]:
            msg = self.get_message(
                task="swot-analysis", competitor_name=competitor, context=""
            )
            swot_report = self.get_response(
                response_schema=SWOTAnalysis, message=msg, repetetion_penalty=0.46
            )
            final_report[competitor] = swot_report
        return json.loads(json.dumps(final_report))
