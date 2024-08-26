from openai import OpenAI

class OpenAIConnection:
    client = OpenAI(api_key = "sk-proj-zgtHiETf3CcyWejoDrbQT3BlbkFJarWP3i5v3b1vJ9BILNX0")

    @staticmethod
    def create_paragraph(messages):
        response = OpenAIConnection.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=1,
            max_tokens=4096,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        paragraph = response.choices[0].message.content
        return paragraph

    @staticmethod
    def last_question(json):
        response = OpenAIConnection.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=json,
            temperature=1,
            max_tokens=4096,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        
        question = response.choices[0].message.content
        
        return question
    
    @staticmethod
    def conversation(conversation, json, final_json, question, answer):
        
        conversation[question] = answer
        
        json.append({
            "role": "assistant",
            "content": question
        })
        json.append({
            "role": "user",
            "content": answer
        })
        final_json.append({
            "role": "assistant",
            "content": question
        })
        final_json.append({
            "role": "user",
            "content": answer
        })
        
        question = OpenAIConnection.last_question(json) 
        
        return conversation, json, final_json, question
                            
    def initialize(language):
        json = [
            {
            "role": "system",
            "content": f"To effectively gather information on an idea or experience, it's important to analyze the preceding conversation for continuity. Develop questions that encourage specific and detailed yet concise responses. Structure your inquiries to receive answers limited to one or two words. Never ask for descriptions of any kind; instead, ask questions designed to be answered in no more than two words. Following the initial question, \"What would you like to express today?\", proceed with \"What type of (previous answer) would you like to share?\". If the user is describing an experience, always make sure to ask when and where (in different questions). Always have in mind that these questions are meant to facilitate the creation of a narrative based on the shared experiences or ideas (the narrative creation itself is not required here, don't do it). Gather as much information as you can, names, places, feelings etc. Continuously evaluate the need for additional information. If no further details are necessary, end with the question, \"Would you like to add anything else?\" if the answer is yes, you will eventually have to ask this again until the answer is no, ensure to ask at least twenty questions (counter=(count number of previous answers)), or more if necessary. If the answer to the final question is no, respond with \"{language[9]}\", just this anything else. Don't include the previous answers in the questions. The first question is going to set the language of the conversation."
            }
        ]
        final_json=[
            {
            "role": "system",
            "content": "In this task, you'll find a conversation where the assistant is collecting details about a specific topic. Please synthesize all the discussed information into a first-person narrative paragraph as if you were the one answering the questions. Begin the paragraph directly, without introductory phrases like 'based on the information' or 'with the provided information,' etc., The paragraph has to be in the lenguage of the conversation."
            }
        ]
        return json, final_json