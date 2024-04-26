import json
import openai
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
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
                    "content": "You are a helpful and experienced market analyst. Use your intelligence the provided context(if needed) to complete the task, dont make things up. Answer in valid JSON",
                },
                {
                    "role": "user",
                    "content": f"Tell Market share, sales number, growth etc. and SWOT analysis on {kwargs['competitor_name']} as a business.\n\nCONTEXT :\n{kwargs['context']}",
                },
            ]
        else:
            return [None, None]
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

    def remove_stopwords(self, text):
        stop_words = set(stopwords.words("english"))
        words = word_tokenize(text)
        filtered_text = [word for word in words if word.lower() not in stop_words]
        return " ".join(filtered_text)

    def do_analysis(self, industry):
        # get competitors name
        message = self.get_message(
            task="competitors-name", industry=industry, context=""
        )
        competitors_names = self.get_response(
            response_schema=LoS, message=message, repetetion_penalty=0.5
        )["los"]
        final_report = {}
        for competitor in competitors_names[:4]:

            queries = [
                f"Market share, sales number, global presence, of {competitor} in {industry} industry.",
                f"SWOT Strength, weakness, opportunity and threat of {competitor} in {industry} industry.",
            ]

            content = self.remove_stopwords(WebTool().fetch_content(texts=queries))[
                : 4096 * 4
            ]

            clean_content = client.chat.completions.create(
                model="meta-llama/Llama-3-8b-chat-hf",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an information retriever and summarizer,ignore everything you know, return only the factual information regarding the QUERY into a maximum of 500-600 words. Output should be concise chunks of paragraphs or tables or both, ignore links, using the RAW TEXT",
                    },
                    {
                        "role": "user",
                        "content": f"QUERY :\n\n{','.join(queries)}\n\n RAW TEXT :\n\n{content}",
                    },
                ],
                frequency_penalty=0.16,
            )

            msg = self.get_message(
                task="swot-analysis", competitor_name=competitor, context=clean_content
            )
            swot_report = self.get_response(
                response_schema=SWOTAnalysis, message=msg, repetetion_penalty=0.46
            )
            final_report[competitor] = swot_report
        return final_report
