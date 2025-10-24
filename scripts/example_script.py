"""Navigate to nova.amazon.com/act, click 'Learn More', and extract blog title and publication date."""
import os
from pydantic import BaseModel
from nova_act import NovaAct
import json
## Asssume all environment variables are set in the container

class BlogInfo(BaseModel):
    title: str
    publication_date: str | None



# Initialize Nova Act with your starting page.
nova = NovaAct(
    starting_page="https://nova.amazon.com/act",
    headless=True,  # Set to True to run in headless mode
    chrome_channel="chromium"
)

# Running nova.start will launch a new browser instance.
# Only one nova.start() call is needed per Nova Act session.
nova.start()

# Click the 'Learn More' button
nova.act("click the 'Learn More' button")

# Extract the blog title and publication date
result = nova.act(
    "return the title and publication date of the blog post", 
    schema=BlogInfo.model_json_schema()
)

if result.matches_schema:
    print(json.dumps(result.parsed_response, indent=2))
else:
    print(json.dumps({"error": "Could not extract blog information."}, indent=2))


nova.stop()
