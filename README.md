# Gogoro Smart Scooter Expert

Gogoro Smart Scooter Expert is an AI Agent specifically designed for Gogoro scooter owners. The goal is to utilize Generative AI technology to integrate content from various Gogoro Smart Scooter user manuals, creating an intelligent agent that can answer questions related to Gogoro scooters. The content from the user manuals includes text, tables, and images, all of which serve as knowledge sources for the AI Agent. The agent can synthesize these contents to accurately respond to owners' inquiries and clarify incomplete questions through dialogue.

**This project was awarded the "Excellence Award (Best)" in the Gogoro category at the "AIWave: Taiwan Generative AI Applications Hackathon".**

[Project Demo Video](https://github.com/BRlin-o/GSS/assets/34859596/657486f4-76b2-4bc1-a8c8-09ea283afead)

## Project Features

### Streamlit

- **Full-Stack Integration**: Built with Streamlit for both front-end and back-end, providing an interactive chat interface for users to engage with the AI agent, supporting chat history and real-time responses (streaming).

### LangChain

![AI-workflow](https://raw.githubusercontent.com/BRlin-o/GSS/main/images/AI-workflow.png)

- **Agent Construction**: Utilizing LangChain to connect Chat LLM and QA LLM. Here are the use cases for each model:
  - **Chat LLM**: Responsible for interacting with users, recording user information and chat history, guiding users to ask clear questions, and forwarding specific questions to the QA LLM for answers. It also refuses to answer topics unrelated to Gogoro models.
  - **QA LLM**: Handles RAG (Retrieval-Augmented Generation) searches to find corresponding manual content for specific models, providing accurate answers to vehicle-related questions.

### Amazon Bedrock

- **Efficient AI Services**: All AI services are deployed using Amazon Bedrock Serverless, achieving high efficiency, low latency, and low cost. The models used and their application scenarios are as follows:
  - **Claude 3 Sonnet**: The preferred model for Chat LLM, balancing speed and intelligence, driving the AI agent to provide the best user interaction experience.
  - **Claude 3 Haiku / llama 3 70B**: Used to generate accurate responses based on RAG search results.
    - **Haiku**: The fastest responding model in the Claude 3 series, ideal for quickly responding to questions.
    - **llama 3**: Planned for fine-tuning, with support for AWS imported models to seamlessly integrate with the current design pattern.
  - **Cohere Embed Multilingual**: The preferred embedding model for the knowledge base (RAG), helping to retrieve data sources effectively.

## Getting Started

1. Install the necessary packages:
   ```bash
   pip install -r requirements.txt
   ```

2. Launch the Streamlit application:
    ```
    streamlit run app/streamlit_app.py
    ```

## System Architecture

### Simple Version

![Architecture-Simple](https://raw.githubusercontent.com/BRlin-o/GSS/main/images/Architecture-Simple.png)

### Future Vision

![Architecture-Future](https://raw.githubusercontent.com/BRlin-o/GSS/main/images/Architecture-Future.png)

## Contact
For any questions or suggestions, please contact us via:

- Email: brend.main@gmail.com
- GitHub Issues: [Issues Page](https://github.com/BRlin-o/GSS/issues)

## License
This project is licensed under the MIT License. See the LICENSE file for more details.
