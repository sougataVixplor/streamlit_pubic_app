#@title chat with agent
import os
import weaviate
# from weaviate.classes.init import Auth
# from weaviate.agents.query import QueryAgent
import json

# from weaviate_agents.classes import QueryAgentCollectionConfig


from google import genai
from typing import List
# import pdfplumber
import re
import json
# import fitz

weaviate_url = os.environ["WEAVIATE_URL"]
weaviate_api_key = os.environ["WEAVIATE_API_KEY"]
headers = {
    # Provide your required API key(s), e.g. Cohere, OpenAI, etc. for the configured vectorizer(s)
    "gemini_api_key": os.environ["GEMINI_API_KEY"],
}
from tempfile import template
import json
def str_to_json(output):
  if "null" in output:
    output=output.replace("null","'None'")
  start = output.find('[')
  end = output.rfind(']') + 1
  dict_str = output[start:end]
  data_dict=json.loads(dict_str)
  return data_dict
def get_final_data(user_prompt):

  client = weaviate.connect_to_weaviate_cloud(
    cluster_url=weaviate_url,
    auth_credentials=Auth.api_key(weaviate_api_key),
    headers=headers
  )
  # print(user_prompt)
  agent = QueryAgent(
    client=client,
    collections=[
      QueryAgentCollectionConfig(
        name="FalconPricebook",
        target_vector=[
          "text2vecweaviate",
        ],
      ),
    ],
  )

  query = user_prompt

  result = agent.ask(query)
  # result.display()
  client.close()
  res=json.loads(result.model_dump_json())
  # print(res["final_answer"])
  try:
    final_json_answer=json.loads(res["final_answer"])
  except:
    final_json_answer=str_to_json(res["final_answer"])
  print(final_json_answer)

  return final_json_answer




