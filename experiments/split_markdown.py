from langchain_text_splitters import MarkdownHeaderTextSplitter
import markdown

MARKDOWN_FILE = "CrossOver.md"
OUTPUT_DIR = "output_split_metadata"


# load markdown document with markdown package
with open(MARKDOWN_FILE, "r", encoding="utf-8") as f:
    markdown_document = f.read()

headers_to_split_on = [
    ("#", "Car Type"),
    ("##", "Header 2"),
    ("###", "Header 3"),
    ("####", "Header 4"),
    ("#####", "Header 5"),
    ("######", "page")
]

# MD splits
markdown_splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=headers_to_split_on, strip_headers=False
)
md_header_splits = markdown_splitter.split_text(markdown_document)





for i, split in enumerate(md_header_splits):
    
    pass
# Char-level splits
from langchain_text_splitters import RecursiveCharacterTextSplitter

chunk_size = 400
chunk_overlap = 30
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=chunk_size, chunk_overlap=chunk_overlap
)

# Split
splits = text_splitter.split_documents(md_header_splits)
splits


# Save splits
import os, json

os.makedirs(OUTPUT_DIR, exist_ok=True)

for i, split in enumerate(splits):
    print(f"Split {i}:")
    print(f"Page_content: {split.page_content}")
    print(f"MetaData: {split.metadata}")
    print(f"json: {split.to_json()}")
    
    # Save split to JSON
    #with open(os.path.join(OUTPUT_DIR, f"split_{i}.json"), "w", encoding="utf-8") as f:
    #    json.dump(split.to_json(), f, indent=2, ensure_ascii=False)

    # Save split to .txt and .json
    with open(os.path.join(OUTPUT_DIR, f"split_{i}.txt"), "w", encoding="utf-8") as f:
        f.write(split.page_content)
    
    metadata = {"metadataAttributes": split.metadata}
    
    with open(os.path.join(OUTPUT_DIR, f"split_{i}.txt.metadata.json"), "w", encoding="utf-8") as f:
        
        json.dump(metadata, f, indent=2, ensure_ascii=False)
