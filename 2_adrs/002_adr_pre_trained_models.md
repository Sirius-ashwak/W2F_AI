# ADR002 - Use of Google's Gemini Pre-trained Models for Savour

## Status  
Accepted  

## Context and Problem Statement  
Savour requires a pre-trained multimodal model to understand user queries, pre-process recipes and assess ingredient quality and recipe suitability.

### Requirements  
- High accuracy in understanding diverse and complex language inputs.  
- Ability to adapt and improve using domain-specific data via both in-context learning and/or fine-tuning.
- Minimized time-to-market and development costs.  

### Business and Technical Assumptions  
- Pre-trained models will provide a baseline of advanced capabilities, requiring only minimal fine-tuning for domain-specific contexts.  
- In-house model development is extremely resource-intensive and unnecessary given the availability of state-of-the-art pre-trained models.  
- Licensing and integration of external models will be manageable within the project’s constraints. 

## Decision Drivers  
- Performance: Models must deliver state-of-the-art NLU capabilities.  
- Cost-efficiency: Minimize time and resources spent on model development.  
- Scalability: The chosen approach must support growing demands and evolving use cases.  
- Flexibility: Ability to fine-tune or customize for domain-specific requirements.

## Considered Options  

### 1. In-house Large Language Model (LLM)  
- **Advantages:** Complete control over the model’s architecture and data, no dependency on external providers.  
- **Disadvantages:** Huge development costs, time-intensive, requires extensive computational resources and expertise.

### 2. Pre-trained Models (e.g. Google’s Gemini) (Selected Option)  
- **Advantages:** Access to state-of-the-art NLU capabilities, reduced development time, and fine-tuning options for domain-specific needs.  
- **Disadvantages:** Dependence on external providers, token costs, and limited control over underlying architecture.

### 3. Open-Source Pre-trained Models (e.g., Cohere, Llama)  
- **Advantages:** Secure and open-source. Data is not sent to external providers.
- **Disadvantages:** May lack seamless integration features or preferred licensing terms. Large hosting costs and reduced performance.

## Decision  
Pre-trained models, such as Google’s Gemini 2.0 Flash and Gemini 1.5 Pro - 002, will be used. These models will be used as-is with no fine-tuning, as the goal is to leverage the latest advancements in NLU without the need to develop custom models. Fine-tuning will be reserved for future work to increase domain-specific accuracy and relevance.

Furthermore, the choice of pre-trained models will be made based on the required capabilities and the cost-benefit analysis. For example, image analysis and agentic reasoning will require Gemini 2.0 Flash, while relatively simpler tasks will be handled by Gemini 1.5 Pro - 002.

### Reasons  
- Proven performance with state-of-the-art benchmarks.  
- Significantly reduced development time compared to building in-house models.  
- Flexibility to fine-tune for specific business requirements.  
- Cost-effective when compared to the computational and human resource needs of custom model development.  

## Consequences  

### Positive Impacts  
- Faster deployment of AI capabilities.  
- Access to advanced, continuously improving model architectures.  
- Lower development costs compared to building in-house solutions.  
- Easier scalability with managed service offerings from Google.

### Trade-offs and Limitations  
- Dependence on external providers for updates and maintenance.  
- Licensing and usage costs associated with pre-trained models.  
- Limited control over the underlying architecture and core model functionality.  
