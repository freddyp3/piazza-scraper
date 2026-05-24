from dotenv import load_dotenv
from piazza_api import Piazza
from markdownify import markdownify as md
import os
import json

def load_config():
    load_dotenv()
    email = os.getenv("PIAZZA_EMAIL")
    password = os.getenv("PIAZZA_PASSWORD")
    network_id = os.getenv("PIAZZA_NETWORK_ID_CPSC310_2025W2")
    return (email, password, network_id)

def html_to_md(html):
    if html is None:
        return ""
    return md(html)

def format_post(post):
    output = ""
    post_title = html_to_md(post["history"][-1]["subject"])
    post_content = html_to_md(post["history"][-1]["content"])
    tags = post["tags"]

    # YAML frontmatter
    output += "---\n"
    output += "post_number: " + str(post["nr"]) + "\n"
    output += "title: \"" + post_title.strip() + "\"\n"
    output += "type: " + post["type"] + "\n"
    output += "date: " + post["created"][:10] + "\n"
    output += "folders: " + json.dumps(post.get("folders", [])) + "\n"
    output += "tags: " + json.dumps(tags) + "\n"
    output += "---\n\n"

    output += post_title + "\n" + post_content + "\n"
    output += format_children_helper(post["children"])

    return (post_title, output)

def normalize_type_of_post(type):
    if type == "question":
        return "Question"
    elif type == "note":
        return "Note"
    return "unidentified type of post: " + type

def normalize_response(response):
    if response == "s_answer":
        return "Student Answer"
    elif response == "i_answer":
        return "Instructor Answer"
    elif response == "followup":
        return "Follow Up"
    elif response == "feedback":
        return "Reply to Follow Up"
    return "unidentified response: " + response

def format_children_helper(children):
    output = ""
    while children:
        current = children.pop(0)
        type_of_response = current["type"]

        if type_of_response == "s_answer" or type_of_response == "i_answer":
            response = html_to_md(current["history"][-1]["content"])
        else:
            response = html_to_md(current["subject"])

        if current["children"]:
            children = current["children"] + children

        normalized_response = normalize_response(type_of_response)
        output += "\n" + normalized_response + ": " + response

    return output

# returns list of (start, end) index tuples for image markdown in the string
def img_indices(md_string):
    copy = md_string
    indices = []
    offset = 0
    while copy and copy.find("![") != -1:
        start_index = copy.index("![")
        copy = copy[start_index:]
        end_index = copy.index(")")
        indices.append((start_index + offset, end_index + offset + start_index))
        copy = copy[end_index:]
        offset += start_index + end_index
    return indices

def find_url(img_markdown):
    start = img_markdown.index("(") + 1
    end = img_markdown.index(")")
    return img_markdown[start:end]

def find_filename(img_markdown):
    url = find_url(img_markdown)
    return url.split("%2F")[-1]

# downloads images and replaces piazza urls with local paths
def format_imgs(formatted_post, session):
    indices = img_indices(formatted_post)
    os.makedirs("output/images", exist_ok=True)

    for start_index, end_index in indices:
        img_markdown = formatted_post[start_index:end_index + 1]
        url = find_url(img_markdown)
        filename = find_filename(img_markdown)
        local_path = "output/images/" + filename

        response = session.get("https://piazza.com" + url)
        with open(local_path, "wb") as f:
            f.write(response.content)

        formatted_post = formatted_post.replace(url, local_path)

    return formatted_post

if __name__ == "__main__":
    email, password, network_id = load_config()

    p = Piazza()
    p.user_login(email, password)
    network = p.network(network_id)

    post = network.get_post(11)

    title, formatted_post = format_post(post)
    formatted_post = format_imgs(formatted_post, p._rpc_api.session)

    os.makedirs("output/md_files", exist_ok=True)
    with open("output/md_files/test.md", "w") as f:
        f.write(formatted_post)