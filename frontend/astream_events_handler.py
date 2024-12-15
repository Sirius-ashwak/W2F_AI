from langchain_core.messages import AIMessage
from backend.core.agents.graph import app

async def invoke_graph(st_messages, st_placeholder, config):
    """
    Asynchronously processes a stream of events from the graph_runnable and updates the Streamlit interface.

    Args:
        st_messages (list): List of messages to be sent to the graph_runnable.
        st_placeholder (st.beta_container): Streamlit placeholder used to display updates and statuses.

    Returns:
        AIMessage: An AIMessage object containing the final aggregated text content from the events.
    """
    # Set up placeholders for displaying updates in the Streamlit app
    container = st_placeholder  # This container will hold the dynamic Streamlit UI components
    thoughts_placeholder = container.container()  # Container for displaying status messages
    token_placeholder = container.empty()  # Placeholder for displaying progressive token updates

    # Stream events from the graph_runnable asynchronously
    async for events in app.astream({"messages": st_messages}, config=config, stream_mode="values"):
        pass
    token_placeholder.write(events['messages'][-1].content)
    # Return the final aggregated message after all events have been processed
    return AIMessage(content=events['messages'][-1].content), events['is_clear_enough']