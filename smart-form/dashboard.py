import streamlit as st

st.set_page_config(page_title="Smart Form Dashboard", layout="wide")

"""
prepopulate based on user location
dropdowns to remove user typing wrong inputs
"""

if __name__ == "__main__":
    st.title("📋 Smart Form Dashboard")
    st.markdown("---")
    st.subheader("User Information")

    proc_type = st.radio(
        "Procurement Type", ["E", "F"], index=None, horizontal=True)

    if proc_type == "F":
        pure_f = st.radio(
            "Pure F", ["Yes", "No"], index=None, horizontal=True)

        if pure_f == "Yes":
            # Send email for PIR if not available
            """
            If PIR not available
                Send email for PIR if not available
                Store current form data in S3 bucket
            If PIR available
                ...
            """
            pass
        elif pure_f == "No":
            sto = st.radio(
                "STO", ["Yes", "No"], index=None, horizontal=True)

            if sto == "Yes":
                # PP243 + SPEC PRD COSTING
                """
                .
                """
                pass
            elif sto == "No":
                # SUB CON
                """
                .
                """
                pass

    elif proc_type == "E":
        """
        .
        """
        pure_f = st.radio(
            "Pure F", ["Yes", "No"], index=None, horizontal=True)

        if pure_f == "Yes":
            # Send email for PIR if not available
            pass
        elif pure_f == "No":
            sto = st.radio(
                "STO", ["Yes", "No"], index=None, horizontal=True)

            if sto == "Yes":
                # PP243 + SPEC PRD COSTING
                pass
            elif sto == "No":
                # SUB CON
                pass

    st.markdown("---")

    col5, col6, col7 = st.columns([1, 1, 2])
    with col5:
        submit = st.button(
            "Submit", use_container_width=True)
    with col6:
        clear = st.button(
            "Clear", use_container_width=True)

    if submit:
        if not name:  # check for end branches
            st.error("❌ Please fill in all fields")
        else:
            st.success("✅ Form submitted successfully!")

            with st.expander("View Submitted Data"):
                st.json({
                    "proc_type": proc_type,
                    "selected_option": e_option if proc_type == "E" else f_option,
                    "name": name,
                    "email": email,
                    "age": age,
                    "phone": phone,
                    "birth_date": str(birth_date),
                    "gender": gender,
                    "country": country,
                    "interests": interests,
                    "experience": experience,
                    "salary_range": salary_range,
                    "newsletter": newsletter,
                    "rating": rating,
                    "comments": comments,
                    "file_uploaded": file.name if file else None
                })
