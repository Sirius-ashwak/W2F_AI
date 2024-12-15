# ADR003 - Use LangChain and LangGraph as the Language Model Orchestration Framework

## Status  
Accepted  

## Context and Problem Statement  
The Savour application requires a robust framework for orchestrating multi-step, multi-modal tasks. The framework must allow for defining and managing complex workflows involving multi-step interactions, conditional logic, and advanced contextual handling. The challenge is to choose a framework that supports these needs while ensuring scalability and efficient implementation.  

### Requirements  
- Support for structured orchestration of multi-step, multi-modal tasks.  
- Flexibility to define complex workflows with conditional logic and branching.  
- Scalability to manage increasing complexity and volume of tasks.  
- Familiarity among team members for efficient adoption and use.  
    
### Business or Technical Assumptions  
- Workflow orchestration is critical for managing the assistant’s multi-step, conditional tasks.  
- The team has prior experience with LangChain and LangGraph, which reduces onboarding time and implementation effort.  

## Decision Drivers  
- Workflow management: The framework must simplify the orchestration of multi-step interactions and handle complex logic.  
- Scalability: It must scale effectively with increasing workflow complexity and system demands.  
- Team familiarity: A known framework accelerates development and minimizes learning curves.  

## Considered Options  

### 1. CrewAI  
- **Advantages:** Provides tools for collaborative AI scenarios, potentially useful for team-based workflows.  
- **Disadvantages:** Lacks robust support for structuring complex orchestration tasks.  

### 2. AutoGen  
- **Advantages:** Strong automation features for managing tasks and workflows.  
- **Disadvantages:** Less focused on user-defined, structured orchestration, limiting flexibility for complex logic.  

### 3. Haystack  
- **Advantages:** Open-source and flexible for NLP tasks.  
- **Disadvantages:** Focuses on search and document pipelines, lacking native support for structured orchestration of model interactions.  

### 4. LangGraph (Selected Option)  
- **Advantages:** Designed specifically for structured language model orchestration, supporting complex workflows with branching and conditional logic. Team familiarity accelerates implementation. Excellent community support and ecosystem, such as LangChain, LangSmith, and LangServe.
- **Disadvantages:** Relatively more complex than other options, potentially requiring additional learning and effort to master.

### 5. Google Agent Builder
- **Advantages:** Simple to use and integrate with Google's AI services. Scalable and easy to deploy.
- **Disadvantages:** Limited flexibility in certain cases.

## Decision  
LangChain and LangGraph are selected as the language model orchestration framework due to its support for structured workflows, advanced contextual handling, and alignment with team expertise.  

### Reasons  
- Offers robust tools for managing complex, structured orchestration of language model tasks.  
- Simplifies the definition of conditional logic and multi-step workflows.  
- Familiarity among team members reduces development time and onboarding challenges.  
- Scales effectively to handle increasing complexity in workflows and interactions.  

## Consequences  

### Positive Impacts  
- Improved ability to define and manage complex, conditional workflows.  
- Accelerated implementation due to team familiarity with the framework.  
- Enhanced scalability for supporting future system demands.  

### Trade-offs and Limitations  
- Requires additional development effort to design and implement complex workflows.  