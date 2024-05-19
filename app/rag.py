from langchain.chains import RetrievalQA
from langchain_community.retrievers import AmazonKnowledgeBasesRetriever
from dotenv import load_dotenv
load_dotenv()

def get_rag_chain(kb_id, llm, car_model=None):
    _car_model = car_model.replace("CrossOver", "Crossover").replace("VIVA", "Viva").replace("XL", "Xl").replace("MIX", "Mix").replace("JEGO", "Jego").replace("S1", "S1 / 1").replace("S2", "S2 / 2").replace("S3", "S3 / 3")
    _car_model = f"Gogoro {_car_model}"
    print("[DEBUG] car_model", _car_model)
    retriever = AmazonKnowledgeBasesRetriever(
        knowledge_base_id=kb_id,
        retrieval_config={
            "vectorSearchConfiguration": {
                "numberOfResults": 6,
                "filter": {
                    "equals": { "key": "Car Type", "value": _car_model }
                }
            }
        },
    )

    return RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        input_key="question",
    )