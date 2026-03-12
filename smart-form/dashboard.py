import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from ai_chatbot import analyse_enquiry

load_dotenv()

st.set_page_config(page_title="Smart Form Dashboard", layout="wide")

# """
# prepopulate based on user location
# dropdowns to remove user typing wrong inputs
# """


def display_bom():
    st.subheader("Bill of Materials (BOM)")

    # Initialize BOM items in session state
    if 'bom_items' not in st.session_state:
        st.session_state.bom_items = [{"id": 0}]

    # Initialize BOM lock state
    if 'bom_locked' not in st.session_state:
        st.session_state.bom_locked = False

    # Item categories for dropdown
    item_categories = ["CU structure element",
                       "Document item",
                       "PM structure element",
                       "Class item",
                       "Stock item",
                       "Intra material",
                       "Non-stock item",
                       "Variable-size item",
                       "Text item",
                       "Drawing"]

    # Display each BOM item
    for idx, item in enumerate(st.session_state.bom_items):
        with st.container():
            st.markdown(f"**Item {idx + 1}**")
            col1, col2, col3, col4 = st.columns([2, 2, 1, 1])

            with col1:
                st.markdown("**Item Category**")
                item_category = st.selectbox(
                    "Item Category",
                    item_categories,
                    key=f"category_{item['id']}",
                    label_visibility="collapsed",
                    placeholder="Select Item Category",
                    disabled=st.session_state.bom_locked
                )

            with col2:
                st.markdown("**Item Code**")
                component = st.text_input(
                    "Component",
                    key=f"component_{item['id']}",
                    label_visibility="collapsed",
                    placeholder="Enter Component",
                    disabled=st.session_state.bom_locked
                )

            with col3:
                st.markdown("**Quantity**")
                quantity = st.number_input(
                    "Quantity",
                    min_value=1,
                    value=1,
                    key=f"quantity_{item['id']}",
                    label_visibility="collapsed",
                    disabled=st.session_state.bom_locked
                )

            with col4:
                if len(st.session_state.bom_items) > 1:
                    if st.button("🗑️", key=f"remove_{item['id']}", help="Remove item", disabled=st.session_state.bom_locked):
                        st.session_state.bom_items.pop(idx)
                        st.rerun()

            # st.markdown("---")

    # Add new item button
    if st.button("➕ Add Item", use_container_width=True, disabled=st.session_state.bom_locked):
        new_id = max([item['id']
                      for item in st.session_state.bom_items]) + 1
        st.session_state.bom_items.append({"id": new_id})
        st.rerun()

    # Lock and Submit BOM button
    st.markdown("")  # Add spacing
    if not st.session_state.bom_locked:
        if st.button("🔒 Lock & Submit BOM", use_container_width=True, type="primary"):
            # Validate all BOM items have filled values
            validation_errors = []

            for idx, item in enumerate(st.session_state.bom_items):
                item_num = idx + 1

                # Check if item category is selected
                category_key = f"category_{item['id']}"
                if category_key not in st.session_state or not st.session_state[category_key]:
                    validation_errors.append(
                        f"Item {item_num}: Item Category is required")

                # Check if component/item code is filled
                component_key = f"component_{item['id']}"
                if component_key not in st.session_state or not st.session_state[component_key].strip():
                    validation_errors.append(
                        f"Item {item_num}: Item Code is required")

                # Quantity is always filled due to default value, but we can check if it's valid
                quantity_key = f"quantity_{item['id']}"
                if quantity_key not in st.session_state or st.session_state[quantity_key] < 1:
                    validation_errors.append(
                        f"Item {item_num}: Quantity must be at least 1")

            if validation_errors:
                st.error("❌ Please fill in all required fields before locking:")
                for error in validation_errors:
                    st.error(f"  • {error}")
            else:
                st.session_state.bom_locked = True
                st.success("✅ BOM items locked and submitted!")
                st.rerun()
    else:
        col_unlock, col_status = st.columns([1, 2])
        with col_unlock:
            if st.button("🔓 Unlock BOM", use_container_width=True):
                st.session_state.bom_locked = False
                st.rerun()
        with col_status:
            st.info("✓ BOM is locked")


# Initialize OpenAI client
if 'client' not in st.session_state:
    st.session_state.client = OpenAI()

# Initialize chat history
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []


if __name__ == "__main__":

    # Sidebar Chatbot
    with st.sidebar:
        st.title("💬 AI Assistant")
        st.markdown(
            "Ask questions about procurement types, processes, or form guidance.")

        # Display chat history
        chat_container = st.container(height=400)
        with chat_container:
            for message in st.session_state.chat_history:
                with st.chat_message(message["role"]):
                    st.write(message["content"])

        # Chat input
        user_input = st.chat_input("Type your question here...")

        if user_input:
            # Add user message to history
            st.session_state.chat_history.append(
                {"role": "user", "content": user_input})

            # Get AI response
            with st.spinner("Thinking..."):
                ai_response = analyse_enquiry(
                    st.session_state.client,
                    user_input,
                    use_rag=True
                )

            # Add AI response to history
            st.session_state.chat_history.append(
                {"role": "assistant", "content": ai_response})

            # Rerun to update chat display
            st.rerun()

        # Clear chat button
        if st.button("Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()

    st.title("📋 Smart Form Dashboard")
    st.markdown("---")
    st.subheader("User Information")

    proc_type = st.radio(
        "Procurement Type", ["E", "F"], index=None, horizontal=True)

    if proc_type == "F":
        # """
        # Is it a stock transport?
        # yes or no
        # """

        # """
        # if yes
        # send email to notify other plant to add the plant connection
        # with new code connection, select special procurement type

        # can be calculated automatically from the other plant response
        #     calculate and upload planned price for 2/3
        # set code automatically based on response
        #     include special procurement costing

        # end
        # """

        # """
        # if no
        # is it subcontract?
        # yes or no
        # """

        # """
        # if yes
        # another BOM exact same
        # slightly different, PIR contact sourcing department
        # calculate planned price 3

        # end
        # """

        # """
        # if no
        # down pure F yes route

        # contact sourcing department

        # get response
        # costs

        # """

        sto = st.radio(
            "Is it a stock transport?", ["Yes", "No"], index=None, horizontal=True)

        if sto == "Yes":
            # Send email for PIR if not available
            """
            If PIR not available
                Send email for PIR if not available
                Store current form data in S3 bucket
            If PIR available
                ...
            """
            pass
        elif sto == "No":
            sto = st.radio(
                "STO", ["Yes", "No"], index=None, horizontal=True)

            if sto == "Yes":
                # PP243 + SPEC PRD COSTING
                # """
                # .
                # """
                pass
            elif sto == "No":
                # SUB CON
                # """
                # .
                # """
                pass

    elif proc_type == "E":
        display_bom()

        st.markdown("---")
        st.subheader("Special Procurement")

        phantom = st.radio(
            "Is this a Phantom?", ["Yes", "No"], index=None, horizontal=True)

        if phantom == "No":
            # Need routing - how long to build
            st.markdown("**Routing Required**")
            build_hours = st.number_input(
                "How long to build? (hours)",
                min_value=0.0,
                step=0.5,
                format="%.1f",
                help="Enter the number of hours required to build"
            )

        elif phantom == "Yes":
            # Check if it's a spare
            is_spare = st.radio(
                "Is this a spare?", ["Yes", "No"], index=None, horizontal=True)

            if is_spare == "Yes":
                # Do a routing (same as before)
                st.markdown("**Routing Required**")
                build_hours = st.number_input(
                    "How long to build? (hours)",
                    min_value=0.0,
                    step=0.5,
                    format="%.1f",
                    help="Enter the number of hours required to build"
                )
            elif is_spare == "No":
                # Nothing needed
                st.info(
                    "No additional routing required for non-spare phantom items.")

    st.markdown("---")

    col5, col7 = st.columns([1, 2])
    with col5:
        submit = st.button(
            "Submit", use_container_width=True)

    if submit:
        # Validation for proc_type == "E" branch
        if proc_type == "E":
            missing_fields = []

            # Check if BOM is locked
            if not st.session_state.get('bom_locked', False):
                missing_fields.append("BOM must be locked and submitted")

            # Check phantom selection
            if phantom is None:
                missing_fields.append("Phantom selection")
            elif phantom == "No":
                # Check build_hours
                if 'build_hours' not in locals() or build_hours == 0.0:
                    missing_fields.append("Build hours")
            elif phantom == "Yes":
                # Check is_spare selection
                if 'is_spare' not in locals() or is_spare is None:
                    missing_fields.append("Spare selection")
                elif is_spare == "Yes":
                    # Check build_hours for spare
                    if 'build_hours' not in locals() or build_hours == 0.0:
                        missing_fields.append("Build hours")

            if missing_fields:
                st.error(
                    f"❌ Please fill in all required fields: {', '.join(missing_fields)}")
            else:
                st.success("✅ Form submitted successfully!")
        else:
            st.success("✅ Form submitted successfully!")
