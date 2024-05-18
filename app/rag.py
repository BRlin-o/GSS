from langchain.chains import RetrievalQA
from langchain_community.retrievers import AmazonKnowledgeBasesRetriever
from dotenv import load_dotenv
load_dotenv()


def get_rag_chain(kb_id, llm, car_model=None):
    print("[DEBUG] car_model", car_model)
    _car_model = car_model.replace("VIVA", "Viva").replace("XL", "Xl").replace("MIX", "Mix")
    retriever = AmazonKnowledgeBasesRetriever(
        knowledge_base_id=kb_id,
        retrieval_config={
            "vectorSearchConfiguration": {
                "numberOfResults": 4,
                "filter": {
                    "equals": { "key": "Car Type", "value": f"Gogoro {_car_model}" }
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