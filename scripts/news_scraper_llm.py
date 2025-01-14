import os
import warnings
import pandas as pd
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain.indexes import VectorstoreIndexCreator

from send_email import send_email
from google_news_scraper import scrape_news
import logging

logging.basicConfig(
    filename="C:\\Users\\tee_m\\Desktop\\TIC3901 Indus Project\\scripts\\script.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.info("Script started.")

warnings.filterwarnings("ignore")

os.environ["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY")
    
keywords = ["global+news+today", "financial+markets", "fixed+income+markets", "currencies+markets", "equities+markets", "commodities+markets", "emerging+markets", "politics", "economics"]

scrape_news(keywords)

csv_file_path = "C:\\Users\\tee_m\\Desktop\\TIC3901 Indus Project\\scripts\\google_news.csv"
df = pd.read_csv(csv_file_path)

llm = ChatOpenAI(model="gpt-4", temperature=0)

# Initialize embedding model and index creator
embedding_model = OpenAIEmbeddings()
index_creator = VectorstoreIndexCreator(embedding=embedding_model)

# Initialize combined summary
combined_summary = ""

# Process each column in the DataFrame
for col in df.columns:
    logging.info(f"Processing column: {col}")
    
    # Combine column content into a single text string
    column_text = " ".join(df[col].dropna().astype(str))
    
    # Write column text to a temporary file
    temp_text_file = f"C:\\Users\\tee_m\\Desktop\\TIC3901 Indus Project\\scripts\\text\\{col}_cleaned_text.txt"
    with open(temp_text_file, "w", encoding="utf-8") as temp_file:
        temp_file.write(column_text)
    
    # Load the text into the LLM pipeline
    loader = TextLoader(temp_text_file, encoding="utf-8")
    index = index_creator.from_loaders([loader])
    
    # Query the LLM
    query = """Using the provided context, provide a detailed and exhaustive analysis. Include:
    - Comprehensive explanations with elaboration on critical points.
    - Ensure the response is structured with clear sections or bullet points for readability.
    """
    
    response = index.query(question=query, llm=llm)
    
    # Append the response to the combined summary
    combined_summary += f"\nTopic: {col}\n{response}\n"
    logging.info(f"Completed processing for column: {col}")


output_file_path = "C:\\Users\\tee_m\\Desktop\\TIC3901 Indus Project\\scripts\\summary.txt"
with open(output_file_path, "w", encoding="utf-8") as file:
    file.write(combined_summary)

logging.info("Processing completed. Combined summary saved.")
print("Combined Summary saved to:", output_file_path)

send_email("Using the provided context, highlight in-depth details with direct references to the context.", combined_summary)