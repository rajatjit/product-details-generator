import json
import re
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import Settings, StorageContext, VectorStoreIndex
from llama_index.core import SimpleDirectoryReader
import openai
from config import OPENAI_API_KEY
from web_search import google_search

def generate_product_details(brand, item_number, name, id1):

    #Build a search query based on the product identifiers
    search_q = f"{brand} {item_number} {name}"
    results = google_search(search_q, num_results=8)

    #Turn them into a little “browser context” blob
    browser_context = "\n".join(
    f"- {r['title']}: {r['snippet']} ({r['link']})"
    for r in results
    )

    openai.api_key = OPENAI_API_KEY
    if not openai.api_key or openai.api_key == "your-api-key-here":
        raise RuntimeError("Invalid OpenAI API")

    prompt = f"""
    You are an expert product researcher and technical writer specializing in automotive parts. Your task is to gather, verify, and synthesize detailed product information for a list of products. For each product, you will:
    look up the details based on 
    - Brand: {brand}
    - Item Number: {item_number}
    - Name: {name}
    - ID: {id1}
    
    You have this local documentation (RAG context) plus these web snippets: {browser_context}

    Please generate the following information in JSON format:

    Generate a Detailed Response: 
    Format your response to display the product information on screen. The response should include: 

    {{
      "Internal Reference": "Copy the same {item_number} as it to this field e.g. HRT36700NT225",
      "Name": "e.g. 90.0/11/0-15NLMT 2.25",
      "Specifications": " Create a list of Brand, Item Number, Tire Size, Tread Patter, Tread Pattern, Tread Width, Approx. Diameter, Approx Circumference, Recommended Rim Width, Measured Rim Width, Section Width, Compund and return in json format with the values of each parameter",
      "eCommerce Description": "Write a short description of the product. Also get the information from any other resources from the internet."
      "Disclaimer": "Write a one line disclaimer for the product. Include anykind of warnings that are relevant to product. Also get the information from any other resources from the internet.",
      "Description": "Write a long in-detail description of the product. Mention what is the product used for, what are its benefits etc. Also get the information from any other resources from the internet."
      "ID": "Copy the same {id1} as it to this field e.g. "__export__.product_template_140625_01c00637""
    }}  

    Make sure to use the provided information to create detailed, accurate product descriptions and response should be in json format.
    """
    llm = None
    Settings.llm = OpenAI(
        model="gpt-3.5-turbo",
        temperature=1,
        max_tokens=3000
    )
    documents = SimpleDirectoryReader("./data/").load_data()
    storage_context = StorageContext.from_defaults()


    Settings.embed_model = OpenAIEmbedding(
        model="text-embedding-ada-002",
        request_timeout=120
    )

    index = VectorStoreIndex.from_documents(
        documents=documents,
        storage_context=storage_context
    )
    query_engine = index.as_query_engine(
    similarity_top_k=5,
    streaming=False
    )
    
    try:
        response = query_engine.query(prompt)
        if not response:
            print("No response received from LLM.")
            return None
            
        content = str(response)
        if not content:
            print("Empty response received from LLM.")
            return None
        
        # Try to parse the JSON response
        try:
            details = json.loads(content)
            return details
        except json.JSONDecodeError:
            print("Failed to parse JSON from LLM response. Attempting to extract information manually.")
            
            # Extract information using regex patterns
            details = {}

            # Extract Internal Reference
            internal_reference_match = re.search(r'"Internal Reference":\s*"([^"]*)"', content)
            if internal_reference_match:
                details["Internal Reference"] = internal_reference_match.group(1)
            else:
                details["Internal Reference"] = ""  
            
            # Extract Product Name
            product_name_match = re.search(r'"Name":\s*"([^"]*)"', content)
            if product_name_match:
                details["Name"] = product_name_match.group(1)
            else:
                details["Name"] = "" 

             # Extract Specification
            spec_match = re.search(r'"Specifications":\s*"([^"]*)"', content)
            if spec_match:
                details["Specifications"] = spec_match.group(1)
            else:
                details["Specifications"] = ""
            
            # Extract eCommerce Description
            eCom_desc_match = re.search(r'"eCommerce Description":\s*"([^"]*)"', content)
            if eCom_desc_match:
                details["eCommerce Description"] = eCom_desc_match.group(1)
            else:
                details["eCommerce Description"] = ""
                
            # Extract Disclaimer
            disclaimer_match = re.search(r'"Disclaimer":\s*"([^"]*)"', content)
            if disclaimer_match:
                details["Disclaimer"] = disclaimer_match.group(1)
            else:
                details["Disclaimer"] = ""
            
            # Extract Description
            desc_match = re.search(r'"Description":\s*"([^"]*)"', content)
            if desc_match:
                details["Description"] = desc_match.group(1)
            else:
                details["Description"] = ""
            
            # Extract ID
            id_match = re.search(r'"ID":\s*"([^"]*)"', content)
            if id_match:
                details["ID"] = id_match.group(1)
            else:
                details["ID"] = ""

            # If we couldn't extract any information, return None
            if not any(details.values()):
                print("Could not extract any information from the response.")
                print(f"Raw response: {content}")
                return None
                
            return details
            
    except Exception as e:
        print(f"Error generating product details: {e}")
        return None
