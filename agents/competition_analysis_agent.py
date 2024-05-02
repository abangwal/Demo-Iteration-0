import json
import openai
from tools.web_tool import WebTool
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from schemas import LoS, SWOTAnalysis, About, Timeline
import tiktoken

client = openai.OpenAI(
    base_url="https://api.together.xyz/v1",
    api_key="",
)


class CompetitorAnalyst:
    def __init__(self):
        self.encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

    def get_message(self, task, **kwargs):
        if task == "web-query":
            message = [
                {
                    "role": "system",
                    "content": "You are a helpful assistant. Use your own intelligence to complete the task.",
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
                    "content": "You are a helpful assistant. Use your own intelligence and the provided context(if needed) to complete the task. Answer in provided JSON schema.",
                },
                {
                    "role": "user",
                    "content": f"Name mojor competitors in the {kwargs['industry']} business.\n\nCONTEXT :\n{kwargs['context']}",
                },
            ]
        elif task == "swot-analysis":
            message = [
                {
                    "role": "system",
                    "content": "You are a helpful and experienced market analyst. Use your own intelligence and the provided context(if needed) to complete the SWOT analysis for the given company, dont make things up. Dont use Markdown and Answer in provided JSON schema",
                },
                {
                    "role": "user",
                    "content": f"Do SWOT analysis on {kwargs['competitor_name']} as a business.\n\nCONTEXT :\n{kwargs['context']}",
                },
            ]
        elif task == "timeline":
            message = [
                {
                    "role": "system",
                    "content": "You are a helpful researcher. Use your own intelligence and the provided context(if needed) to find the timeline of events about the given company, dont make things up. Dont use Markdown or other formating and Answer in provided json schema",
                },
                {
                    "role": "user",
                    "content": f"Tell events and achievement happened with {kwargs['competitor_name']} as a business in correct order.\n\nCONTEXT :\n{kwargs['context']}",
                },
            ]
        elif task == "about":
            message = [
                {
                    "role": "system",
                    "content": "You are a helpful assistant. Use your own intelligence and the provided context(if needed) to find the description about a company and products and services provided by company, dont make things up. Dont use Markdown or other formating and Answer in provided json schema",
                },
                {
                    "role": "user",
                    "content": f"Tell description about {kwargs['competitor_name']} as a company and few products or services offer by {kwargs['competitor_name']} along with their pricing.\n\nCONTEXT :\n{kwargs['context']}",
                },
            ]
        else:
            message = [None, None]
        return message

    def limit_tokens(self, input_string, token_limit=8000):

        return self.encoding.decode(self.encoding.encode(input_string)[:token_limit])

    def get_response_helper(self, response_schema, message, repetetion_penalty):
        response = client.chat.completions.create(
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            messages=message,
            response_format={
                "type": "json_object",
                "schema": response_schema.model_json_schema(),
            },
            frequency_penalty=repetetion_penalty,
        )
        content = json.loads(response.choices[0].message.content)
        return content

    def get_response(self, competitor, industry, task, query, schema):
        content = self.remove_stopwords(text=WebTool().fetch_content(texts=[query]))

        trimmed_content = self.limit_tokens(input_string=content)
        clean_content = client.chat.completions.create(
            model="meta-llama/Llama-3-8b-chat-hf",
            messages=[
                {
                    "role": "system",
                    "content": "You are an information retriever and summarizer,ignore everything you know, extract all the factual information regarding the QUERY into a maximum of 300-400 words. Output should be plain text no markdown or formatting just chunks of paragraph full of information, ignore links, using the RAW TEXT",
                },
                {
                    "role": "user",
                    "content": f"QUERY :\n\n{query}\n\n RAW TEXT :\n\n{trimmed_content}",
                },
            ],
            frequency_penalty=0.1,
        )

        msg = self.get_message(
            task=task,
            industry=industry,
            competitor_name=competitor,
            context=clean_content.choices[0].message.content,
        )

        report = self.get_response_helper(
            response_schema=schema, message=msg, repetetion_penalty=0.23
        )

        return report

    def remove_stopwords(self, text):
        stop_words = set(stopwords.words("english"))
        words = word_tokenize(text)
        filtered_text = [word for word in words if word.lower() not in stop_words]
        return " ".join(filtered_text)

    def do_analysis(self, industry):
        # get competitors name
        competitors_name_query = f"Names of top competitors in the {industry} industry."
        competitors_names = self.get_response(
            schema=LoS,
            task="competitors-name",
            query=competitors_name_query,
            industry=industry,
            competitor="",
        )["los"]
        final_report = {}
        for competitor in competitors_names[:2]:

            queries = [
                f"SWOT Strength, weakness, opportunity and threat of {competitor} in {industry} industry.",
                f"Events and achievements of {competitor} in {industry} industry, like investments, sales records, returns, etc.",
                f"About the {competitor} and the products or services offer by {competitor} in {industry}.",
            ]

            swot_report = self.get_response(
                industry=industry,
                competitor=competitor,
                task="swot-analysis",
                query=queries[0],
                schema=SWOTAnalysis,
            )
            final_report[competitor] = swot_report

            about_report = self.get_response(
                industry=industry,
                competitor=competitor,
                task="timeline",
                query=queries[1],
                schema=Timeline,
            )
            final_report[competitor].update(about_report)

            products = self.get_response(
                industry=industry,
                competitor=competitor,
                task="about",
                query=queries[2],
                schema=About,
            )
            final_report[competitor].update(products)

        return final_report
