# Repository for RAG Project

This repository contains all the necessary files to run the Retrieval-Augmented Generation (RAG) project.

## Project Overview

In this project, we fine-tuned the **Llama-3-8b-instruct** model on **Google Colab** using a custom dataset stored in `data.json`. The fine-tuned model was saved to **Hugging Face** for potential use. However, due to performance constraints when running the fine-tuned model locally, we implemented the RAG pipeline using the **Llama-3-70b-chat-hf** model, hosted online on **Together.ai**.

A video demonstration of the **Gradio** app has been uploaded to this repository, showcasing the interactions with the Large Language Model (LLM), where messages and contextual information are sent, and the model responds accordingly.

---

## Workflow

### 1. **Data Extraction**

- The source data is extracted from the [ROS 2 Documentation GitHub Repository](https://github.com/ros2/ros2_documentation).
- The repository's text files are cleaned and stored in **MongoDB**.
- Coding files are also stored in MongoDB _without any preprocessing_. All other non-text files in the repository are ignored.

### 2. **Storing Data in MongoDB**

- Each file is saved in MongoDB along with metadata such as:
  - `file_name`
  - `url`
  - `repo_name`

### 3. **Chunking and Embedding Creation**

- The extracted data is divided into smaller chunks.
- Each chunk is converted into a 300-dimensional embedding vector.
- These embeddings, along with their associated payloads, are stored in the **Qdrant Vector Database**.

### 4. **Query Processing**

- When a user submits a query, the following steps are performed:
  1. Retrieve the 5 most similar embeddings from Qdrant based on the query.
  2. Create a prompt consisting of:
     - A **system message**
     - The **user query**
     - The **retrieved context** from Qdrant.

### 5. **Generating a Response**

- The constructed prompt is sent to the LLM.
- The LLM processes the prompt and generates a response.
- The response is displayed to the user via the **Gradio** interface.

---

## Files in the Repository

1. **`data.json`**  
   Contains the custom dataset used for fine-tuning the model.

2. **`fine_tuning_notebook.ipynb`**  
   The Python notebook used for fine-tuning the **Llama-3-8b-instruct** model.

3. **`fine_tuning_notebook.ipynb`**  
   The Python notebook used for fine-tuning the **Llama-3-8b-instruct** model.

4. **`Embedding_demo.ipynb`**  
   The Python notebook used to demonstrate
   the embedding process.

5. **`Extraction_demo.ipynb`**  
   The Python notebook used to demonstrate
   the data extraction process.

6. **`llm_connection.ipynb`**  
   The Python notebook used to demonstrate
   retrieval and response from the llm.

7. **Gradio App Video**  
   A video showcasing the working of the Gradio interface for user interactions with the RAG system.

8. **Screenshots**  
   This folder has the screenshots of the
   work done to complete this project.

9. **Docker Files**  
   Docker files to run the project.

---

## How to Run

1. Clone the repository.
2. Build the container using: docker build -t ai_demo_run_1 .
3. Run the docker compose file.
4. create a docker network using this command: docker network create my_network
5. Run mongodb container on this network: docker run -d --name mongodb --network my_network -p 27017:27017 mongo:5.0
6. Run qdrant container on this network: docker run -d --name qdrant --network my_network -p 6333:6333 qdrant/qdrant:v1.3.0
7. Run the app container using your clearml credentials:
   docker run -p 8501:8501 -e CLEARML_API_ACCESS_KEY=YOUR_API_KEY -e CLEARML_API_SECRET_KEY=YOUR_API_SECRET -e CLEARML_API_HOST=YOUR_SERVER_URL ai_demo_run_1
8. Then open the gradio app on your browser and run the initialize database command to start the etl pipeline, and initialize a qdrant vector database.
9. Finally you can ask questions to the LLM.

---

This repository covers the full RAG workflow, demonstrating the use of modern tools to efficiently retrieve context-aware responses using LLMs.
