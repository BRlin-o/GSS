# Gogoro 萬事通

這是一個為Gogoro車主量身打造的AI助手：Gogoro Smart Scooter萬事通，目標是使用 Generative AI 技術，匯整 Gogoro Smart Scooter 各車種車主手冊的內容，製作成一個可以回答 Gogoro 車
主 Smart Scooter 相關問題的 Agent。車主手冊內容包含文字、表格與圖像，均是 Agent 可取用的知識/ 資訊來源。此外，不同車種的車主手冊內容，有同也有異，Agent 須統整這些內容，精準回答車主的提問，甚至車主的提問可能不完整，Agent 可透過與車主對話來釐清問題與回答。

## 專案特色

### Streamlit

- 使用Streamlit建構前後端，提供Chat介面讓車主與Agent可以交互、聊天紀錄，另外支援LLM即時回應(streaming)

### LangChain

![AI-workflow](https://raw.githubusercontent.com/BRlin-o/GSS/main/images/AI-workflow.png)

使用LangChain建構Agent串接Chat LLM and QA LLM，以下是各模型的應用場景與說明：

- Chat LLM：負責與車主交互，記錄車主資訊與對話記錄，引導幫助車主問出好的問題，將明確的問題拋給QA LLM進行解答，且能拒絕回覆任何Gogoro車型以外的話題。
- QA LLM：負責針對問題進行RAG檢索，找出該問題對應車型的手冊內容，準確地回答車輛相關問題。

### Amazon Bedrock

- 以上所有AI服務都使用Amazon Bedrock Serverless服務，達到高效、低延遲、低成本，以下是使用到的模型以及應用場景
  - Claude 3 Sonnet：Sonnet是Claude 3系列中，相對平衡速度與智能的模型，是我們Chat LLM的首選，最適合用來根據使用者的需求，來驅動我們的Agent，實現最好的使用者交互體驗。
  - Claude 3 Haiku / llama 3 70B：根據RAG檢索出的相關內容，對問題作出準確的答覆。
    - Haiku是Claude 3系列提供回應速度最快的模型，因為僅需根據RAG檢索內容回答問題，因此響應速度越快能夠越早將結論回應給Chat LLM。
    - llama 3是另外我們想做fine-tuning，同時也看到AWS前幾天在Amazon Bedrock上支援了imported model，讓我們可以把自己訓練好的模型上傳，在系統端可以直接透過bedrock的窗口進行使用，因此也能無痛接軌我們目前的Design Pattern。
  - Cohere Embed Multilingual：作為我們knowledge base(RAG)首選的embedding Model，用來幫助我們對Data Source進行檢索

## 系統架構

### 簡易版
![Architecture-Simple](https://raw.githubusercontent.com/BRlin-o/GSS/main/images/Architecture-Simple.png)
### 未來展望
![Architecture-Future](https://raw.githubusercontent.com/BRlin-o/GSS/main/images/Architecture-Future.png)
## 開始使用

```
pip install -r requirements.txt
streamlit run app/chat_agent.py
```