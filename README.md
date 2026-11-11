# 🎈 Blank app template

A simple Streamlit app template for you to modify!

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://blank-app-template.streamlit.app/)

### How to run it on your own machine

1. Install the requirements

   ```
   $ pip install -r requirements.txt
   ```

2. Run the app

   ```
   $ streamlit run streamlit_app.py
   ```

### Nightscout URL

The app only fetches `https://` URLs that point to public addresses.
If you run the app on your own machine and your Nightscout instance is on
`http://localhost` or in your private network, start it with
`NIGHTSCOUT_ALLOW_LOCAL_URLS=1`:

```
$ NIGHTSCOUT_ALLOW_LOCAL_URLS=1 streamlit run streamlit_app.py
```

Do not set this variable on a public deployment.
