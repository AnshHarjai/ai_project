from bs4 import BeautifulSoup
from pymongo import MongoClient
from clearml import Task

import re
import os
import shutil
import subprocess
import tempfile


# Initialize ClearML task
task = Task.init(project_name="RAG_ETL_Project", task_name="ETL_Pipeline")


# MongoDB Connection
def connect_mongodb():
    """Connect to MongoDB."""
    client = MongoClient("mongodb://mongodb:27017/")
    return client["RAG_DB"], client["RAG_DB"]["raw_data"]


def extract_github(repo_url):
        """Extract content from a GitHub repository."""

        repo_name = repo_url.rstrip("/").split("/")[-1]
        temp_dir = tempfile.mkdtemp()

        try:
            # Clone the repository into a temporary directory
            os.chdir(temp_dir)
            subprocess.run(["git", "clone", repo_url], check=True)

            # Determine the cloned repository's path
            repo_path = os.path.join(temp_dir, os.listdir(temp_dir)[0])

            # Parse files in the repository
            tree = {}
            for root, _, files in os.walk(repo_path):
                dir = root.replace(repo_path, "").lstrip("/")
                if dir.startswith((".git", ".toml", ".lock", ".png")):
                    continue

                for file in files:
                    if file.endswith((".git", ".toml", ".lock", ".png")):
                        continue
                    file_path = os.path.join(dir, file)
                    with open(os.path.join(root, file), "r", errors="ignore") as f:
                        tree[file_path] = f.read()

            data_entry = {
                "content": tree,
                "url": repo_url,
                "source": "github",
                "repo_name": repo_name,
            }

            # self.ingested_urls.append(repo_url)
            return data_entry

        finally:
            # Cleanup temporary directory
            shutil.rmtree(temp_dir)


# Transform Function
def clean_text(raw_text):
    """Clean and process raw text data."""
    soup = BeautifulSoup(raw_text, "html.parser")
    return soup.get_text().strip()


def clean_data(content):
    """Clean raw content for better transformer embeddings."""
    # Remove code blocks (fenced with triple backticks)
    content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
    
    # Remove markdown artifacts like #, *, -, `, and excessive newlines
    content = re.sub(r'[\n#`*\\-]', ' ', content)
    
    # Flatten lists (e.g., "- item" to "item")
    content = re.sub(r'^\s*-\s*', '', content, flags=re.MULTILINE)
    
    # Replace multiple spaces with a single space
    content = re.sub(r'\s+', ' ', content).strip()
    
    # Normalize text (e.g., convert to lowercase)
    content = content.lower()
    
    return content


def transform_data(data):
    """Clean and transform the extracted data."""
    if not data or not data.get("content"):
        print("No content to transform.")
        return None
    else:
        transformed_data = {}
        for file, content in data["content"].items():
            if file.endswith((".md", ".rst", ".txt")):
                transformed_data[file] = {
                    "content": clean_data(clean_text(content)),
                    "file_name": file,
                    "url": data["url"],
                    "source": data["source"],
                    "repo_name": data["repo_name"],
                }
            elif file.endswith((".py", ".cpp", ".c", ".ipynb")):
                transformed_data[file] = {
                    "content": content,
                    "file_name": file,
                    "url": data["url"],
                    "source": data["source"],
                    "repo_name": data["repo_name"],
                }
        return transformed_data


# Load Function
def load_to_mongodb(data, db, collection):
    """Load transformed data into MongoDB."""
    if not data:
        print("No data to load.")
        return

    for file_name, file_data in data.items():
        print(f"Loading {file_name} into MongoDB.")
        collection.update_one(
            {"file_name": file_name},
            {"$set": file_data},
            upsert=True
        )
    print("Data loaded into MongoDB.")


# Main ETL Pipeline
def run_etl(repo_link="https://github.com/ros2/ros2_documentation"):
    """Run the ETL pipeline."""
    db, collection = connect_mongodb()
    if db is None or collection is None:
        print("MongoDB connection failed.")

    # Extract
    github_data = extract_github(repo_link)

    # Transform
    transformed_data = transform_data(github_data)
    print("Transformed GitHub Data:\n", transformed_data)

    # Load
    load_to_mongodb(transformed_data, db, collection)


# if __name__ == "__main__":
#     run_etl()
