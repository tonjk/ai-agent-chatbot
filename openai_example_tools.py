from openai import OpenAI
client = OpenAI()

response = client.responses.create(
  model="gpt-4.1",
  input=[],
  text={
    "format": {
      "type": "json_schema",
      "name": "response_with_images",
      "strict": True,
      "schema": {
        "type": "object",
        "properties": {
          "response": {
            "type": "string",
            "description": "Textual response."
          },
          "images": {
            "type": "array",
            "description": "List of image URLs.",
            "items": {
              "type": "string",
              "description": "URL of an image."
            }
          }
        },
        "required": [
          "response",
          "images"
        ],
        "additionalProperties": False
      }
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
