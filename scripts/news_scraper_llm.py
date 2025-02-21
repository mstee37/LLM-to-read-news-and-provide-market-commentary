import os
import warnings
import pandas as pd
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain.indexes import VectorstoreIndexCreator

from send_email import send_email_v2
from google_news_scraper import scrape_news
import logging

# Remove all existing handlers
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

logging.basicConfig(
    filename="C:\\Users\\tee_m\\Desktop\\TIC3901 Indus Project\\scripts\\market_commentary.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.info("Script started.")

warnings.filterwarnings("ignore")

os.environ["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY")
    
keywords = [
    "global+news+today", "financial+markets", "fixed+income+markets", 
    "currencies+markets", "equities+markets", "commodities+markets", 
    "emerging+markets", "politics", "economics", "bond+issuances",
    "corporate+deals"
]

scrape_news(keywords)

csv_file_path = "C:\\Users\\tee_m\\Desktop\\TIC3901 Indus Project\\scripts\\google_news.csv"
df = pd.read_csv(csv_file_path)

llm = ChatOpenAI(model="gpt-40", temperature=0)

# Initialize embedding model and index creator
embedding_model = OpenAIEmbeddings()
index_creator = VectorstoreIndexCreator(embedding=embedding_model)

# Initialize combined summary
combined_summary = ""

txt_file_paths = []

# Process each column in the DataFrame
for col in df.columns:
    logging.info(f"Processing column: {col}")
    
    # Combine column content into a single text string
    column_text = " ".join(df[col].dropna().astype(str))
    
    # Write column text to a temporary file
    temp_text_file = f"C:\\Users\\tee_m\\Desktop\\TIC3901 Indus Project\\scripts\\text\\{col}_cleaned_text.txt"
    txt_file_paths.append(temp_text_file)
    with open(temp_text_file, "w", encoding="utf-8") as temp_file:
        temp_file.write(column_text)
    
    # # Load the text into the LLM pipeline
    # loader = TextLoader(temp_text_file, encoding="utf-8")
    # index = index_creator.from_loaders([loader])
    
    # # Query the LLM
    # query = """Using the provided context, provide a detailed and exhaustive analysis. Include:
    # - Comprehensive explanations with elaboration.
    # - Ensure the response is structured with clear sections or bullet points for readability.
    # """
    
    # response = index.query(question=query, llm=llm)
    
    # # Append the response to the combined summary
    # combined_summary += f"\nTopic: {col}\n{response}\n"
    
    
    
    # TODO: AKU NO MONEY TO USE LLM
    with open(temp_text_file, "r", encoding="utf-8") as file:
        txt = file.read()
    
    combined_summary += f"\nTopic: {col}\n{txt}\n"
    logging.info(f"Completed processing for column: {col}")


output_file_path = "C:\\Users\\tee_m\\Desktop\\TIC3901 Indus Project\\scripts\\summary.txt"
with open(output_file_path, "w", encoding="utf-8") as file:
    file.write(combined_summary)

logging.info("Processing completed. Combined summary saved.")
print("Combined Summary saved to:", output_file_path)

# Print the list of file paths
# print(txt_file_paths)

send_email_v2(
    subject="Market Commentary",
    query="Using the provided context, highlight in-depth details with direct references to the context.",
    response=combined_summary,
    attachments=txt_file_paths
)