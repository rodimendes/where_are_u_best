import streamlit as st


st.set_page_config(
    page_title="Contact",
    page_icon="📬",
    layout="centered",
)

# TODO https://www.buymeacoffee.com/rodimendesM
st.markdown("# Keep in touch with me")

st.markdown("[![Foo](https://logospng.org/download/linkedin/logo-linkedin-256.png)](https://www.linkedin.com/in/rodrigo-mendes-pinto/)")


with st.form(key="form"):
    text = st.text_area("Feel free to give me some impressions or suggestions.")
    st.form_submit_button()
