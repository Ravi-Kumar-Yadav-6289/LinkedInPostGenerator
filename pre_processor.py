import json
from llm_helper import llm
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
import re


def sanitize_text(text):
    # Remove invalid surrogate pairs
    return re.sub(r"[\ud800-\udfff]", "", text)


def call_llm(prompt, input_content):
    pt = PromptTemplate.from_template(prompt)
    chain = pt|llm
    response = chain.invoke(input={'input_content':input_content})

    try:
        json_parser = JsonOutputParser()
        resp = json_parser.parse(response.content)
    except OutputParserException:
        raise OutputParserException("Context too big. Unable to parse jobs.")
    return resp


def normalize_tags(posts):
    unique_tags=set()
    for post in posts:
        unique_tags.update(post['tags'])

    unique_tags_list = ','.join(unique_tags)
    print(unique_tags_list)
    template = '''I will give you a list of tags. You need to unify tags with the following requirements,
    1. Tags are unified and merged to create a shorter list. 
       Example 1: "Jobseekers", "Job Hunting" can be all merged into a single tag "Job Search". 
       Example 2: "Motivation", "Inspiration", "Drive" can be mapped to "Motivation"
       Example 3: "Personal Growth", "Personal Development", "Self Improvement" can be mapped to "Self Improvement"
       Example 4: "Scam Alert", "Job Scam" etc. can be mapped to "Scams"
    2. Output should be a JSON object, No preamble
    3. Output should have mapping of original tag and the unified tag. 
       For example: {{"Jobseekers": "Job Search",  "Job hunting": "Job Search", "Motivation": "Motivation}}
       *Important: The key in the above dictionary should remain same as the original text.
    Here is the list of tags: 
    {input_content}
    '''
    resp = call_llm(template, unique_tags_list)
    print(resp)
    return resp



def extract_meta(post_content):
    template = '''
    You are given a LinkedIn post. You need to extract number of lines, language of the post and maximum 2 tags.
    1. Return a valid JSON. No preamble. 
    2. JSON object should have exactly three keys: line_count, language and tags. 
    3. tags is an array of text tags. Extract maximum two tags.
    4. Language should be English or Hinglish (Hinglish means hindi + english)
    Here is the actual post on which you need to perform this task:  
    {input_content}
    '''

    resp = call_llm(template,post_content)
    return resp


def preProcess(raw_file, processed_file=None):
    with open(raw_file,encoding='UTF-8') as file:
        posts = json.load(file)
        enriched_posts = []
        for post in posts:
            post['text'] = sanitize_text(post['text'])
            metadata = extract_meta(post['text'])
            enriched_posts.append(post|metadata)
            
    unified_tags = normalize_tags(enriched_posts)
    unified_tags={key.lower(): value for key, value in unified_tags.items()}
    for epost in enriched_posts:
        curr_tags=epost['tags']
        new_tags = {unified_tags[tag.lower()] for tag in curr_tags}
        epost['tags'] = list(new_tags)
    with open(processed_file, encoding='utf-8', mode="w") as outfile:
        json.dump(enriched_posts, outfile, indent=4, ensure_ascii = False)



if __name__=="__main__":
    preProcess(r"D:\LLMs\groc\data\raw_data.json",r"D:\LLMs\groc\data\pre_processed_data.json")