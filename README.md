## 📖 **Overview**
<img src="images/common/savour_banner.png" alt="Savour Banner" width="500" height="auto"/>

### About Savour

Food waste squanders critical land and water resources and creates unnecessary greenhouse gas emissions in the context of a cost of living crisis. This is not just an economic issue - it is an environmental challenge that demands innovative solutions. 

Savour confronts food waste at the source, turning the problem into an opportunity for sustainable and healthy living. By reimagining how households interact with ingredients, recipes, and their environmental footprint, Savour leverages cutting-edge AI to transform your kitchen into a smart, eco-friendly hub.

---

### 🌟 **Team Members** 

Hi! We are the **"Savour Team"**.

-  **[Kenichi Nakanishi](https://www.linkedin.com/in/kenichinakanishi)**  
-  **[Ikumi Nakanishi](https://www.linkedin.com/in/ikumi-nakanishi-b40622130/)**  
-  **[Viola Wing Yin Chan](https://www.linkedin.com/in/viola-chan-158a834b/)** 

---

## 🚀 **Features and Roadmap** 

### Features
📄 [View Features and Roadmap](3_features_and_roadmap/features_and_roadmap.md)  
Lists all the features of the Web Based AI Assistant System.

---

## 🔷 **Architecture and Design** 

### C4 Architecture

Provides an [end-to-end architectural view](1_architecture_and_design/architecture.md)   of the Savour application.

<img src="images/architecture/c4-architecture-savour.png" alt="C4 Architecture Diagram" width="500" height="auto"/>

---

## 📊 **Architecture Decision Records (ADRs)** 

Explore the rationale behind critical architectural decisions in the project.  

### ADRs List

-  📄 [ADR Template](2_adrs/000_adr_template.md)  
-  📄 [NoSQL Database Storage](2_adrs/001_adr_nosql_database_storage.md)  
-  📄 [Pre-Trained Models](2_adrs/002_adr_pre_trained_models.md)  
-  📄 [LangChain and LangGraph Frameworks](2_adrs/003_adr_langchain_langgraph_framework.md)  
-  📄 [LLMOps Platform](2_adrs/004_adr_llmops_platform.md)

---

## ⚙️ **Setup Instructions**

Create a file `savour/backend/core/local/envs/.env.dev`   with the following environment variables:

```
# Google Cloud Project Settings
PROJECT_ID=your-gcp-project-id
LOCATION=your-gcp-region  # e.g., us-central1

# MongoDB Atlas Configuration
MONGODB_ATLAS_CLUSTER_URI=mongodb+srv://username:password@your-cluster-url/?retryWrites=true&w=majority&appName=YourAppName

# Reddit API Credentials
REDDIT_USER=your-reddit-client-id
REDDIT_SECRET=your-reddit-client-secret
REDDIT_USERNAME=your-reddit-username
REDDIT_PASSWORD=your-reddit-password

# LangSmith Configuration
LANGCHAIN_API_KEY=your-langchain-api-key
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_PROJECT=your-project-name
LANGCHAIN_TRACING_V2=true
```

### How to obtain the credentials:
#### Google Cloud Project (LLMs and Hosting):
* Create a project in Google Cloud Console
* Note your project ID and preferred region
#### MongoDB Atlas (Database and Vector Search):
* Sign up for MongoDB Atlas
* Create a cluster and get your connection string
* Replace username, password, and cluster URL with your credentials
#### Reddit API (r/recipes scraping):
* Go to Reddit's App Preferences
* Create a new application to get client ID and secret
* Use your Reddit account username and password
#### LangSmith (LLMOps):
* Sign up for LangSmith
* Create a new project
* Get your API key from the settings page

