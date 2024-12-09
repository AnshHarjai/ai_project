import etl_pipeline as etl
import featurization_pipeline as featurization
import retrieve_from_qdrant as retrieve
import llm_connection as llm
import gradio as gr


def chat(query):
    # Run the retrieval pipeline
    if query == "Initialize Database":
        etl.run_etl()
        featurization.run_featurization_pipeline()
        return "Database initialized successfully!"
    
    search_results = retrieve.run_retrieve_pipeline(query)
    context = ""
    for res in search_results:
        context += res['chunk'] + " "
    
    # Create the prompt
    prompt = llm.create_prompt(query, context)
    
    print("prompt: ")
    print(prompt)
    print("*"*100, "\n")
    
    # Get the response
    response = llm.get_response(prompt)
    return response

def combined_input(dropdown_input, text_input):
    # Use the text input if provided, otherwise use the dropdown input
    if text_input:
        return text_input
    return dropdown_input

# Create the Gradio interface
iface = gr.Interface(
    fn=lambda dropdown_input, text_input: chat(combined_input(dropdown_input, text_input)),
    inputs=[
        gr.Dropdown(
            ["Tell me how can I navigate to a specific pose - include replanning aspects in your answer.", 
             "Can you provide me with code for navigating to a specific pose?",
             "Initialize Database",
             ],
            label="Sample Questions",
            type="value",
            interactive=True
        ),
        gr.Textbox(
            placeholder="Or type your own question here...",
            label="Your Question",
            interactive=True
        )
    ],
    outputs="text",
    title="Chat with LLM",
    description="Select a sample question or type your own query and get a response from the language model."
)

iface.launch(server_name="0.0.0.0", server_port=7860)