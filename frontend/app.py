import streamlit as st 
import base64
from backend.core.env import LANGCHAIN_API_KEY, LANGCHAIN_ENDPOINT, LANGCHAIN_PROJECT
import pandas as pd
from loguru import logger
from langchain_core.messages import HumanMessage, AIMessage
from frontend.astream_events_handler import invoke_graph
import uuid
import asyncio
from backend.core.agents.extract_ingredients_node import extract_ingredients_node
from backend.core.tools.recipe_search import retrieve_recipes
from backend.preprocessing.preprocessing_enums import DifficultyLevel
from backend.core.agents.extract_ingredients_node import assess_ingredient_node
from backend.preprocessing.preprocessing_enums import DIFFICULTY_MAP, COOKING_METHOD_MAP, MEAL_TYPE_MAP, COURSE_TYPE_MAP, CLEANUP_EFFORT_MAP
from streamlit_lottie import st_lottie
import json
import os
from PIL import Image
from io import BytesIO

# Set environment variables
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = LANGCHAIN_API_KEY
os.environ["LANGCHAIN_ENDPOINT"] = LANGCHAIN_ENDPOINT
os.environ["LANGCHAIN_PROJECT"] = LANGCHAIN_PROJECT


st.set_page_config(layout="wide")

def load_lottie_local(path):
    with open(path, 'r') as f:
        return json.load(f)

def init_session_state():
    """Initialize session state variables if they don't exist"""
    if "messages" not in st.session_state:
        st.session_state['messages'] = []
    
    if "is_clear_enough" not in st.session_state:
        st.session_state['is_clear_enough'] = False
    
    if "ingredients" not in st.session_state:
        st.session_state['ingredients'] = []

    if "quantities" not in st.session_state:
        st.session_state['quantities'] = []

    if "image_files" not in st.session_state:
        st.session_state['image_files'] = []

    if "image_message" not in st.session_state:
        st.session_state['image_message'] = HumanMessage(
                content=[
                    {"type": "text", "text": "Please determine if you can identify all ingredients visible in this image and their approximate quantities."},
                ],
            )
    if "image_list" not in st.session_state:
        st.session_state['image_list'] = []

    if "image_message_added" not in st.session_state:
        st.session_state["image_message_added"] = False
        
    if "messages" not in st.session_state:
        st.session_state['messages'] = []
        
    if "config" not in st.session_state:
        thread_id = str(uuid.uuid4())
        st.session_state["config"] = {
            "configurable": {
                    "thread_id": thread_id,
                }
            }
    if "initial_run" not in st.session_state:
        st.session_state["initial_run"] = False

    if "recipes" not in st.session_state:
        st.session_state["recipes"] = []

    if "image_identification_animation" not in st.session_state: 
        st.session_state["image_identification_animation"] = load_lottie_local("frontend/assets/image_identification.json")

    if "recipe_retrieval_animation" not in st.session_state:
        st.session_state["recipe_retrieval_animation"] = load_lottie_local("frontend/assets/recipe_retrieval.json")

if __name__ == "__main__":
    # Initialize session state
    init_session_state()
    st.image('frontend/assets/savour.png', width=300)
    # Add info blob
    st.success("""
    This is a prototype of the Savour app. 
    It helps you reduce food waste by finding recipes based on the ingredients you have. 
    It uses a combination of Google's Gemini Flash 2.0 and Pro 1.5 multimodal models to identify the ingredients in your image, assess food safety and recommend matching recipes.
    """)
    # Wide layout
    l_col, r_col = st.columns([1,2])

    with l_col:
        st.subheader("Step 1: Upload Image")
        st.markdown("""
        Upload image(s) of the ingredients you want to use!
        """)
        # Store current image files for comparison
        current_image_files = st.file_uploader('', type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)
        
        # Check if image files have changed
        if current_image_files != st.session_state['image_files'] and current_image_files:
            logger.info("Image files have changed")
            # Reset the state variables
            st.session_state['messages'] = []
            st.session_state['image_files'] = current_image_files
            st.session_state["config"] = {
                "configurable": {
                    "thread_id": str(uuid.uuid4()),
                }
            }
            st.session_state['ingredients'] = []
            st.session_state['quantities'] = []
            st.session_state['image_list'] = []
            st.session_state['recipes'] = []
            st.session_state['image_message'].content = [
                {"type": "text", "text": "Please determine if you can identify all ingredients visible in these images and their approximate quantities."}
            ]
            st.session_state["initial_run"] = False
            st.session_state['image_message_added'] = False

        if st.session_state['image_files']:
            for image_file in st.session_state['image_files']:
                # Open image with PIL
                img = Image.open(image_file)
                
                # Calculate new height maintaining aspect ratio
                target_width = 1024
                aspect_ratio = img.size[1] / img.size[0]
                target_height = int(target_width * aspect_ratio)
                
                # Resize image
                im = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
                
                # Convert to RGB mode if necessary
                if im.mode in ('RGBA', 'LA') or (im.mode == 'P' and 'transparency' in im.info):
                    im = im.convert('RGB')
                
                # Save resized image to buffer
                buffered = BytesIO()
                im.save(buffered, format="JPEG", quality=100)  # Using JPEG format
                base64_bytes = base64.b64encode(buffered.getvalue()).decode('utf-8')

                st.image(image_file, caption='Uploaded image(s)', width=400)
                st.session_state['image_message'].content.append(
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_bytes}"},
                        }
                )
                st.session_state['image_list'].append(
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_bytes}"},
                        }
                )
            if not st.session_state['image_message_added']:
                st.session_state['messages'].append(st.session_state['image_message'])
                st.session_state['image_message_added'] = True
                logger.info("Added image message to messages")

        "---"

        if len(st.session_state["image_message"].content) > 1:
            # Capture user input from chat input
            prompt = st.chat_input()
            # Loop through all messages in the session state and render them as a chat on every st.refresh mech
            for msg in st.session_state.messages[1:]:  # skip the image message
                # https://docs.streamlit.io/develop/api-reference/chat/st.chat_message
                # we store them as AIMessage and HumanMessage as its easier to send to LangGraph
                if isinstance(msg, AIMessage):
                    st.chat_message("assistant", avatar="frontend/assets/forkman-face.png").write(msg.content)
                elif isinstance(msg, HumanMessage):
                    st.chat_message("user", avatar="frontend/assets/tomato.png").write(msg.content)
            # Handle user input if provided
            if prompt:
                st.session_state.messages.append(HumanMessage(content=prompt))
                st.chat_message("user", avatar="frontend/assets/tomato.png").write(prompt)
                # Reset the ingredients and quantities if the user has inputted a new prompt
                st.session_state['ingredients'] = []
                st.session_state['quantities'] = []

                with st.chat_message("assistant", avatar="frontend/assets/forkman-face.png"):
                    # create a placeholder container for streaming and any other events to visually render here
                    placeholder = st.container()
                    st.session_state["config"] = {
                        "configurable": {
                            "thread_id": str(uuid.uuid4()),
                        }
                    }
                    response, is_clear_enough = asyncio.run(invoke_graph(st.session_state.messages, placeholder, st.session_state.config))
                    st.session_state['is_clear_enough'] = is_clear_enough
                    st.session_state.messages.append(response)

            if not st.session_state["initial_run"]:
                with st.chat_message("assistant", avatar="frontend/assets/forkman-face.png"):
                    # create a placeholder container for streaming and any other events to visually render here
                    placeholder = st.container()

                    st.session_state["config"] = {
                        "configurable": {
                            "thread_id": str(uuid.uuid4()),
                        }
                    }
                    response, is_clear_enough = asyncio.run(invoke_graph(st.session_state.messages, placeholder, st.session_state.config))

                    st.session_state['is_clear_enough'] = is_clear_enough
                    st.session_state.messages.append(response)
                    # Track that we have run the graph once for the initial image upload
                    st.session_state["initial_run"] = True



        with r_col:
            if st.session_state['is_clear_enough'] and st.session_state['ingredients'] == []:
                # Create a placeholder for the animation
                placeholder = st.empty()

                # Display the loading animation
                with placeholder.container():
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        st_lottie(st.session_state["image_identification_animation"], height=500, width=500)
                        loading_text = st.empty()
                        loading_text.markdown("<h4 style='text-align: center;'>Identifying ingredients...</h4>", unsafe_allow_html=True)

                ingredients_response = extract_ingredients_node(st.session_state.messages)
                st.session_state['ingredients'] = ingredients_response['ingredients']
                st.session_state['quantities'] = ingredients_response['quantities']

                ingredient_inspect_message = HumanMessage(
                        content=[
                            {"type": "text", "text": "Please determine the safety and shelf life of the ingredient."},
                        ],
                    )
                for image in st.session_state['image_list']:
                    ingredient_inspect_message.content.append(image)

                loading_text.markdown("<h4 style='text-align: center;'>Assessing ingredients...</h4>", unsafe_allow_html=True)
                ingredient_assessments_response = asyncio.run(assess_ingredient_node([ingredient_inspect_message], st.session_state['ingredients'], st.session_state['quantities']))
                st.session_state['ingredient_assessments'] = ingredient_assessments_response

                # Replace the animation with results
                placeholder.empty()

            if st.session_state['ingredients']:
                st.subheader("Step 2: Ingredients Zone")
                st.markdown("""
                Here are the ingredients we've identified and their approximate quantities.
                You can edit the quantities and select which ingredients you want to use for the recipe finder.
                """)
                # Create a dataframe from ingredients and quantities
                df = pd.DataFrame({
                    'Ingredient': st.session_state['ingredients'],
                    'Quantity': st.session_state['quantities'],
                    'Safe to Consume': ['✅' if i.is_safe_to_consume else '❌' for i in st.session_state['ingredient_assessments']['assessments']],
                    'Approx. Shelf Life': [i.remaining_shelf_life for i in st.session_state['ingredient_assessments']['assessments']],
                    'Use Ingredient': [False] * len(st.session_state['ingredients']),
                }, index=range(len(st.session_state['ingredients'])))
                # Display as an interactive table
                data_editor = st.data_editor(df, num_rows="dynamic", use_container_width=True)

                # For each ingredient assessment, show the reasoning if it's not is_safe_to_consume
                warnings = []
                for i, assessment in enumerate(st.session_state['ingredient_assessments']['assessments']):
                    if not assessment.is_safe_to_consume:
                        warnings.append(assessment.reasoning)
                if warnings:
                    with st.container(border=True):
                        st.markdown("##### Check your ingredients!")
                        st.warning(icon="🚨", body="\n\n".join(warnings))

                "---"
                st.subheader("Step 3: Recipe Finder Zone")
                st.markdown("""
                Jot down any preferences you have for the recipe, and we'll find you some recipes to try!
                """)
                # Add a text input for the user to enter a query
                query = st.text_input("Enter the kind of dish you want to make")
                # Add a button to find recipes
                col1, col2 = st.columns(2)

                with col1:
                    st.write("Difficulty Level")
                    difficulty_level = st.selectbox(
                        label="Difficulty Level",
                        options=["Any"] + list(DifficultyLevel),
                        format_func=lambda x: x.value.replace('_', ' ').title() if x != "Any" else "Any",
                        label_visibility="collapsed"
                    )
                with col2:
                    st.write("Maximum Time to Cook")
                    max_total_time = st.slider(
                        label="Maximum Time to Cook",
                        min_value=5,
                        max_value=360,
                        value=60,
                        step=5,
                        label_visibility="collapsed",
                        help="Select maximum cooking time",
                        key="max_time_slider",
                        format="%d mins",
                    )
                
                if st.button("Find recipes", use_container_width=True):
                    selected_ingredients = data_editor[data_editor['Use Ingredient'] == True]['Ingredient'].tolist()
                    selected_quantities = data_editor[data_editor['Use Ingredient'] == True]['Quantity'].tolist()
                    ingredients_str = ", ".join([f"{ing} ({qty})" for ing, qty in zip(selected_ingredients, selected_quantities)])
                    if query:
                        prompt = f"I want to make {query} with the following ingredients: {ingredients_str}. Please find me a recipe that uses these ingredients."
                    else:
                        prompt = f"I want to make a recipe with the following ingredients: {ingredients_str}. Please find me a recipe that uses these ingredients."
                    if difficulty_level != "Any":
                        difficulty_level = [DifficultyLevel(difficulty_level)]
                    else: 
                        difficulty_level = None
                    # Create a placeholder for the animation
                    placeholder = st.empty()

                    # Display the loading animation
                    with placeholder.container():
                        col1, col2, col3 = st.columns([1, 2, 1])
                        with col2:
                            st_lottie(st.session_state["recipe_retrieval_animation"], height=500, width=500)
                            recipe_loading_text = st.empty()
                            recipe_loading_text.markdown("<h4 style='text-align: center;'>Finding recipes...</h4>", unsafe_allow_html=True)

                    # Fetch recipes (simulate with the retrieve_recipes function)
                    st.session_state['recipes'] = retrieve_recipes(
                        prompt, 
                        difficulty_level=difficulty_level, 
                        max_total_time=max_total_time
                    )

                    # Replace the animation with results
                    placeholder.empty()

            if st.session_state['recipes']:
                # Remove any duplicate titles
                recipe_set = set()
                recipe_list = []
                for recipe in st.session_state['recipes']:
                    if recipe.metadata['title'] in recipe_set:
                        continue
                    else:
                        recipe_set.add(recipe.metadata['title'])
                        recipe_list.append(recipe)

                # Display the recipes
                st.session_state['recipes'] = recipe_list
                for recipe in st.session_state['recipes']:
                    with st.container(border=True):
                        st.markdown(f"### [{recipe.metadata['title']}]({recipe.metadata['post_url']})")
                        # Add a small image of the recipe, next to the description
                        col1, col2, col3 = st.columns([1, 4, 2])
                        with col1:
                            st.image(recipe.metadata['post_image_url'], use_container_width =True)
                        with col2:
                            st.write(recipe.page_content)
                        with col3:
                            st.write(f"**Cleanup Effort** - {CLEANUP_EFFORT_MAP[recipe.metadata['cleanup_effort']]}")
                            st.write(f"**Cooking Method** - {COOKING_METHOD_MAP[recipe.metadata['cooking_method']]}")
                            st.write(f"**Difficulty Level** - {DIFFICULTY_MAP[recipe.metadata['difficulty_level']]}")
                            st.write(f"**Total Time** - {recipe.metadata['total_time']} minutes")
                            st.write(f"**Course Types** - {', '.join([COURSE_TYPE_MAP[course_type] for course_type in recipe.metadata['course_types']])}")
                            st.write(f"**Meal Types** - {', '.join([MEAL_TYPE_MAP[meal_type] for meal_type in recipe.metadata['meal_types']])}")

                        # # Expander for reasoning
                        # st.write(recipe.metadata['reasoning'])
                        # Expander for detailed recipe
                        with st.expander("Detailed recipe"):
                            st.write(recipe.metadata['display_description'].replace("\\n", "\n"))
