from together import Together

together_ai_api = "21003311b33c7dddadb89d6c0c7b42e81d8e39c866f672692b15a404e32351e6"

def create_prompt(query, context):
    sys_prompt = "You are an AI assistant for a robotics company. Your task is to answer questions about ROS2, Nav2, MoveIt2, and Gazebo. Use the provided data to generate responses for the given question. Your responses should be informative and accurate."
    prompt = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": query, "context": context},
    ]
    return prompt


def get_response(prompt):
    client = Together(api_key=together_ai_api)

    response = client.chat.completions.create(
        model="meta-llama/Llama-3-70b-chat-hf",
        messages=prompt,
        max_tokens=500,
    )

    return response.choices[0].message.content