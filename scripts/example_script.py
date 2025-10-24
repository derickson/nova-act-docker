"""Navigate to nova.amazon.com/act, click 'Learn More', and extract blog title and publication date."""
import os
from pydantic import BaseModel
from nova_act import NovaAct

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

# # Add your nova.act(<prompt>) statement here
# nova.act("Click the Learn More button. Then, return the title and publication date of the blog.")

# Extract the blog title and publication date
result = nova.act(
    "return the title and publication date of the blog post", 
    schema=BlogInfo.model_json_schema()
)

if result.matches_schema:
    blog = BlogInfo.model_validate(result.parsed_response)
    print("Blog Information:")
    print(f"Title: {blog.title}")
    if blog.publication_date:
        print(f"Publication Date: {blog.publication_date}")
    else:
        print("Publication Date: Not found")
else:
    print("Could not extract blog information.")
    print(f"Raw response: {result.response}")

# Leaving nova.stop() commented keeps NovaAct session running.
# To stop a NovaAct instance, press "Restart Notebook" (top-right) or uncomment nova.stop() 
# Note: this also shuts down the browser instantiated by NovaAct so subsequent nova.act() calls will fail.
nova.stop()
