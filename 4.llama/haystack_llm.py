from haystack.nodes import PromptTemplate, PromptNode, PromptModel
from haystack.pipelines import Pipeline

# This is to set up the OpenAI model:
from getpass import getpass

api_key_prompt = "Enter OpenAI API key:" 
api_key = getpass(api_key_prompt)

# Specify the model you want to use:
prompt_open_ai = PromptModel(model_name_or_path="gpt-3.5-turbo-instruct", api_key=api_key)

# This sets up the default model:
prompt_model = PromptModel()

# Now let make one PromptNode use the default model and the other one the OpenAI model:
node_default_model = PromptNode(prompt_model, default_prompt_template="deepset/question-generation", output_variable="questions")
node_openai = PromptNode(prompt_open_ai, default_prompt_template="deepset/question-answering")

pipeline = Pipeline()
pipeline.add_node(component=node_default_model, name="prompt_node1", inputs=["Query"])
pipe.add_node(component=node_openai, name="prompt_node_2", inputs=["prompt_node1"])
output = pipe.run(query="not relevant", documents=[Document("Berlin is the capital of Germany")])
output["results"]