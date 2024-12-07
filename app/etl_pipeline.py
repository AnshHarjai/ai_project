import requests
from bs4 import BeautifulSoup
from pytube import YouTube
from pymongo import MongoClient
from clearml import Task


# Initialize ClearML task
task = Task.init(project_name="RAG_ETL_Project", task_name="ETL_Pipeline")


# MongoDB Connection
def connect_mongodb():
    """Connect to MongoDB."""
    client = MongoClient('mongodb://mongodb:27017/')
    #client = MongoClient('mongodb+srv://rv2459:<gsGfhApsDKXvbf9l>@cluster0.hdugh.mongodb.net/')
    #client = MongoClient('mongodb+srv://rv2459:<gsGfhApsDKXvbf9l>@cluster0.hdugh.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
    return client["RAG_DB"], client["RAG_DB"]["raw_data"]


# Extract Functions
def fetch_github_file(repo_owner, repo_name, file_path="README.md", branch="blob/rolling"):
    """Fetch a file from a GitHub repository."""
    url = f"https://github.com/{repo_owner}/{repo_name}/{branch}/{file_path}"
    url = "https://github.com/ros2/ros2_documentation/blob/rolling/README.md"
    url="https://raw.githubusercontent.com/ros2/ros2_documentation/refs/heads/rolling/README.md"
    response = requests.get(url)
    
    if response.status_code == 200:
        
        return {"source": "GitHub", "url": url, "content": response.text}
    else:
        print(f"Failed to fetch file: {url}. Status Code: {response.status_code}")
        return None


def fetch_youtube_transcript(video_url):
    """Fetch transcript from YouTube video."""
    yt = YouTube(video_url)
    transcript = yt.captions.get_by_language_code('en')  # Fetch English captions
    if transcript:
        return {"source": "YouTube", "url": video_url, "content": transcript.generate_srt_captions()}
    else:
        print("No transcript available for this video.")
        return None


# Transform Function
def clean_text(raw_text):
    """Clean and process raw text data."""
    soup = BeautifulSoup(raw_text, "html.parser")
    return soup.get_text().strip()


def transform_data(data):
    """Clean and transform the extracted data."""
    if not data or not data.get("content"):
        print("No content to transform.")
        return None
    data["content"] = clean_text(data["content"])
    return data


# Load Function
def load_to_mongodb(data, db, collection):
    """Load transformed data into MongoDB."""
    if data:
        try:
            print("Loading Data to MongoDB:\n", data)
            collection.insert_one(data)
            print(f"Data from {data['source']} loaded successfully into MongoDB!")
        except Exception as e:
            print(f"Failed to insert data into MongoDB: {e}")
    else:
        print("No data to load into MongoDB.")


# Main ETL Pipeline
def run_etl():
    """Run the ETL pipeline."""
    db, collection = connect_mongodb()
    if db is None or collection is None:
        print("MongoDB connection failed.")

    # Extract
    #github_data = fetch_github_docs("https://github.com/ros/ros2_documentation/blob/707083cb3ea40458e497ca9704a8cf75aa2f1c1c")
    github_data = fetch_github_file("ros", "ros2_documentation", "README.md")
    print("Extracted GitHub Data:\n", github_data)
    #youtube_data = fetch_youtube_transcript("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

    # Transform
    transformed_data = transform_data(github_data)
    print("Transformed GitHub Data:\n", transformed_data)
    #youtube_data = transform_data(youtube_data)

    # Load
    load_to_mongodb(transformed_data, db, collection)
    #load_to_mongodb(youtube_data, db, collection)


if __name__ == "__main__":
    run_etl()
