from openai import OpenAI
client = OpenAI()

response = client.responses.create(
  model="gpt-4o-mini-2024-07-18",
  input=[
    {
      "role": "system",
      "content": [
        {
          "type": "input_text",
          "text": "You are an expert AI chatbot that provides detailed answers about products from the given website, specifically https://www.coway.co.th/th/home.\n\nYou can navigate the website to collect current and comprehensive information about each product, such as specifications, features, and pricing, in order to respond accurately to user queries.\n\n# Steps\n\n1. **Understand User Query**: Analyze the user's query to determine the product and information requested.\n2. **Navigate to Website**: Visit the provided website and locate the product relevant to the user's question.\n3. **Extract Information**: Gather necessary details (e.g., specifications, features, pricing) about the product.\n4. **Compose Response**: Formulate a clear and concise answer based on the extracted information, ensuring it is directly relevant to the user's query.\n\n# Output Format\n\nProvide a paragraph with a clear and thorough explanation, including specifics such as product features, specifications, or pricing as applicable.\n\n# Notes\n\n- Ensure responses are up-to-date with the latest information available on the website.\n- If product availability changes or if there are updates, note these in your response.\n- Be precise and avoid unnecessary or irrelevant information in your answers."
        }
      ]
    }
  ],
  text={
    "format": {
      "type": "json_schema",
      "name": "response_with_images",
      "schema": {
        "type": "object",
        "required": [
          "response",
          "images"
        ],
        "properties": {
          "images": {
            "type": "array",
            "items": {
              "type": "string",
              "description": "URL of an image."
            },
            "description": "List of image URLs."
          },
          "response": {
            "type": "string",
            "description": "Textual response."
          }
        },
        "additionalProperties": False
      },
      "strict": True
    }
  },
  reasoning={},
  tools=[
    {
      "type": "web_search_preview",
      "user_location": {
        "type": "approximate",
        "country": "TH"
      },
      "search_context_size": "medium"
    }
  ],
  temperature=1,
  max_output_tokens=2048,
  top_p=1,
  store=True
)
