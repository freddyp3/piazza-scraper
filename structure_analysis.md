this is just a markdown file to jot down some analysis notes of the structure of the json output. 

useful fields:
- created
useful because time good be an important part of answering questions.
- history
it is an array. contains the subject and content of the post
- type
the type of post. The only two I have ever seen are note and question. This is still valuable data.
- tags
contains the tags related to the post. Again valuable data. Also include who it was posted by (student, instructor)
- children
  - [0]
    first element of it,
    - history
    contains the first response (either the student response or just general response, in this case it is the students response but we must look into more examples to be sure)
    - type
    type of answer, in this case it is "s_answer" which I can only assume means student's answer
    - [1]
    second element
    - subject
    subject of the follow up discussion
    - type
    in this case it is a "followup"
    - children
    similar to before. has the children thread of responses to the respective followup discussion
    follows the same format as above. so its going to have a subject, type, and it's own children
    - [2]
      - history
    this is the instructor response. 
        - content
        the actual response
      - type
    i_answer


So my overall analysis from this stuff would be that each starts off with it's history which is an array of what the question used is. The only important stuff in this section is subject and content.
then we also have the type of post and the tags.
The last useful field is children, which adds another layer to our json.
This children goes into the responses. 
Each child is each response.
When there is a regular follow up discussion (not a instructor or student response) the useful fields are: subject, type, children. This set of children follows the same format and goes in deeper to any follow ups on the original follow up.
Next there are instructor and student answers. These follow format similar to the actual posted question. It has a history field which holds and array of the history of the response each element having the content field (which is important to us). then that last thing that is important is outside of the history field and that is the type (i_answer or s_answer)
These answers also have children fields however I believe it is impossible nor have I ever seen these special category of responses have children. 

So the logic is that there are three types of children I am going to run through a loop checking if it is either s_answer or i_answer and then scrape based off of that. type is at the base of each child so it is an easy check. 

one added note that Claude told me is that: 
Something you noticed but should make explicit: The history array contains edits. history[0] is the original, history[-1] (last element) is the most recent version. You'll want history[-1] for the current content.