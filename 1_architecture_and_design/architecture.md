# Savour - C4 Architecture

<img src="../images/architecture/c4-architecture-savour.png" alt="C4 Architecture Diagram" width="500" height="auto"/>

This document provides a concise overview of the end-to-end C4 architecture for **Savour**, covering System Context, Containers, and Components.

📄 [View the full architecture here](../images/architecture/c4-architecture-savour.png)

---

# Key Components of Savour Architecture

## C1 - System Context Diagram
- **User:**  
  The person interacting with the Savour web app.
- **Web App:**  
  The main interface where users interact with Savour, backed by AI and the LLMOps platform.
- **LLMOps Platform:**  
  The operational platform monitoring the AI-powered capabilities of the application.

---

## C2 - Container Diagram (Web App)
### 1. Web UI (Streamlit)
- The MVP interface users interact with.
- Communicates with the **User Database** and other subsystems.

### 2. User Database (NoSQL DB)
- Stores customer-specific information such as inventory and preferences.

### 3. Recipe Search
- **Framework:** LangChain + MongoDB.  
- Queries recipes based on ingredients and preferences.
- Retrieves data from the **Recipe Database** (MongoDB instance storing recipe data).

### 4. Ingredient Agent
- Processes user-provided ingredient images.
- Utilizes an **LLM (Gemini)** for analysis.
- Updates the User Database with processed information.

### 5. LLM (Gemini)
- A multi-modal LLM with long-context capabilities.
- Integrated for ingredient analysis and recipe recommendations.

---

## C3 - Container Diagram (Ingredient Agent and Recipe Search)
### Ingredient Agent
1. **Information Gathering (LangChain):**
   - Ensures images are sufficient for processing or requests additional information.
2. **Ingredient Extraction (LangChain):**
   - Extracts structured data from images (e.g., ingredients, quantities).
3. **Ingredient Assessment (Gemini LLM):**
   - Evaluates ingredient quality, safety, and expiration.

### Recipe Search
1. **Filtered Hybrid Vector Search (MongoDB):**
   - Combines metadata filtering with vector search for recipe retrieval.
2. **Aspect Ranking (LangChain):**
   - Ranks recipes by matching ingredient lists and user queries.
3. **Content Refinement (Python Script):**
   - Enhances recipe metadata for improved search accuracy.

---

## Supporting Components
- **Recipe Database (MongoDB):**  
  Stores recipe information, including metadata.
- **Content Refinement (Python Script):**  
  Refines and cleans metadata in the Recipe Database for optimal search results.

---

## Future Enhancements

- **Responsible AI Dashboard**: For ethical and performance metrics visualization.
- **Real-Time Alerts**: To flag anomalies or risks in AI performance.
- **Advanced Fine-Tuning Pipelines**: To improve the assistant's conversational abilities.

---

This modular architecture ensures scalability, flexibility, and adherence to responsible AI practices.
