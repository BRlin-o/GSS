# Gogoro Smart Scooter 萬事通

Gogoro Smart Scooter 萬事通是一款專為 Gogoro 車主設計的 AI Agent，目標是利用生成式 AI 技術，整合各種 Gogoro Smart Scooter 車型的車主手冊內容，製作一個可以回答 Gogoro 車主相關問題的智能Agent。車主手冊內容包括文字、表格和圖像，均為 AI Agent的知識來源。不同車型的手冊內容既有共通性也有差異，AI Agent能統整這些內容，精確回答車主的提問，並能通過與車主的對話澄清不完整的問題。

**這個專案在「雲湧智生｜臺灣生成式AI應用黑客松競賽」Gogoro 組中榮獲「優選獎（最佳）」。**

https://github.com/BRlin-o/GSS/assets/34859596/657486f4-76b2-4bc1-a8c8-09ea283afead


## 專案特色

### Streamlit

- **前後端整合**：使用 Streamlit 建構前後端，提供車主與 AI 代理互動的聊天介面，支持聊天記錄及即時回應 (streaming)。

### LangChain

![AI-workflow](https://raw.githubusercontent.com/BRlin-o/GSS/main/images/AI-workflow.png)

- **Agent 構建**：使用 LangChain 串接 Chat LLM 和 QA LLM，以下是各模型的應用場景與說明：
  - **Chat LLM**：負責與車主互動，記錄車主信息和對話記錄，引導車主提出具體問題，將明確的問題交給 QA LLM 進行解答，並拒絕回答任何與 Gogoro 車型無關的話題。
  - **QA LLM**：負責 RAG 檢索，找出對應車型手冊內容，準確回答車輛相關問題。

### Amazon Bedrock

- **高效 AI 服務**：所有 AI 服務均使用 Amazon Bedrock Serverless 服務，實現高效、低延遲、低成本。以下是使用的模型及其應用場景：
  - **Claude 3 Sonnet**：作為 Chat LLM 的首選模型，平衡速度與智能，驅動 AI 代理提供最佳使用者交互體驗。
  - **Claude 3 Haiku** / **llama 3 70B**：根據 RAG 檢索內容，對問題做出準確答覆。
    - **Haiku**：Claude 3 系列中回應速度最快的模型，適合迅速回應問題。
    - **llama 3**：計劃進行微調，並利用 AWS 提供的 imported model 功能，無縫接軌現有設計模式。
  - **Cohere Embed Multilingual**：作為知識庫 (RAG) 的首選嵌入模型，用於幫助檢索數據來源。

## 安裝與使用

1. 安裝必要套件：
   ```
    pip install -r requirements.txt
   ```
2. 啟動 Streamlit 應用：
   ```
   streamlit run app/streamlit_app.py
    ```


## 系統架構

### 簡易版

![Architecture-Simple](https://raw.githubusercontent.com/BRlin-o/GSS/main/images/Architecture-Simple.png)

### 未來展望

![Architecture-Future](https://raw.githubusercontent.com/BRlin-o/GSS/main/images/Architecture-Future.png)

## 聯絡方式
如有任何問題或建議，請
通過以下方式聯繫我們：

- Email: brend.main@gmail.com
- GitHub Issues: [Issues 頁面](https://github.com/BRlin-o/GSS/issues)

## 授權條款
本專案採用 MIT 授權條款。詳見 LICENSE 文件 了解更多信息。
