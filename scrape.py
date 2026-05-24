from dotenv import load_dotenv
from piazza_api import Piazza
from pprint import pprint
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
    type_of_post = normalize_type_of_post(post["type"])

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
    children = format_children_helper(post["children"])
    
    output += children

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
    elif response ==  "i_answer":
        return "Instructor Answer"
    elif response == "followup":
        return "Follow Up"
    elif response == "feedback":
        return "Reply to Follow Up"
    
    return "unidentified response: " + response

# returns:
#         false if there is no img
#         start and end index if there is (in an array because there can be multiple)
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

def format_children_helper(children):
    output = ""

    while children:
        current = children.pop(0)
        type_of_response = current["type"]
        response = ""
        if type_of_response == "s_answer" or type_of_response == "i_answer":
            response = html_to_md(current["history"][-1]["content"])
        else:
            response = html_to_md(current["subject"])

        if current["children"]:
            children = current["children"] + children

        normalized_response = normalize_response(type_of_response)

        output += "\n" + normalized_response + ": " + response

    return output

# downloads and formats the post's images
def format_imgs(formatted_post, session):
    indices = img_indices(formatted_post)
    os.makedirs("output/images", exist_ok=True)

    for start_index, end_index in indices:
        img_markdown = formatted_post[start_index:end_index + 1]
        url = find_url(img_markdown)
        filename = find_filename(img_markdown)
        local_path = "output/images/" + filename

        # download the image
        response = session.get("https://piazza.com" + url)
        with open(local_path, "wb") as f:
            f.write(response.content)

        # replace piazza url with local path
        formatted_post = formatted_post.replace(url, local_path)

    return formatted_post


def find_url(img_markdown):
    start = img_markdown.index("(") + 1
    end = img_markdown.index(")")
    return img_markdown[start:end]

def find_filename(img_markdown):
    url = find_url(img_markdown)
    return url.split("%2F")[-1]

#    with open("sample.md", "w") as f:
#        json.dump(<whatever>, f, indent=2)

if __name__ == "__main__":
    email, password, network_id = load_config()

    p = Piazza()
    p.user_login(email, password)
    network = p.network(network_id)

    # default post (i_answer, s_answer, followup, feedback)
    post = network.get_post(11)

    # post with image
    #post = network.get_post(11)

    # code to write to file
    #with open("sample_with_img.json", "w") as f:
        #json.dump(post, f, indent=2)
    
    tuple = format_post(post)

    title = tuple[0] # must santize
    formatted_post = tuple[1]

    with open("output/md_files/test.md", "w") as f:
        f.write(format_imgs(formatted_post , p._rpc_api.session))


    


    




