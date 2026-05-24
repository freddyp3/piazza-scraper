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

    output += post_title + "\n" + post_content + "\n" + type_of_post + " | Tags: " + ", ".join(tags)    
    children = format_children_helper(post["children"])
    
    output += children

    return output

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

    pprint(format_post(post))


    


    




