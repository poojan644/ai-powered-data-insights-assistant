# AI-Powered Data Insights Assistant

Upload a CSV/Excel file and get an instant AI-generated analysis: key trends,
anomalies, data quality issues, and follow-up questions worth investigating.
Then ask your own questions about the data in plain English.

Built to show how AI can be layered on top of traditional data analysis
workflows (pandas) rather than replacing them.

## How it works

1. You upload a file → **pandas** computes real statistics (describe, nulls,
   correlations, top categorical values).
2. That statistical summary (not the raw file) is sent to **Claude** with a
   system prompt asking it to reason over the stats like an analyst would.
3. You can then ask follow-up questions in a chat interface, grounded in
   the same summary.

This matters: LLMs are unreliable at scanning raw spreadsheets themselves.
The right pattern is "pandas computes, Claude explains" — this project
demonstrates that pattern.

## Setup

```bash
# 1. Clone and enter the project
git clone <your-repo-url>
cd ai-data-insights

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your API key
cp .env.example .env
# then paste your key from https://console.anthropic.com/settings/keys into .env

# 5. Run it
streamlit run app.py
```

Your browser will open at `http://localhost:8501`.

## Deploying it live (so you have a link, not just code)

1. Push this repo to GitHub (the `.gitignore` already keeps your `.env` out of it).
2. Go to [share.streamlit.io](https://share.streamlit.io), sign in with GitHub.
3. Deploy this repo. In the app's **Settings → Secrets**, add:
   ```
   ANTHROPIC_API_KEY = "sk-ant-your-key-here"
   ```
4. You'll get a public URL like `yourname-ai-data-insights.streamlit.app` —
   put this directly on your resume and LinkedIn.

## What to say about it in interviews

- **"Why did you send a summary instead of the raw data?"** → Cost and
  reliability. Sending thousands of rows wastes tokens and LLMs make
  arithmetic errors scanning raw tables; computing stats with pandas first
  and having Claude reason over them is both cheaper and more accurate.
- **"What would you improve with more time?"** → Add support for the model
  to request specific pandas operations on demand (tool use / function
  calling) instead of relying only on a pre-computed summary, and add
  caching to avoid recomputing insights on every file re-upload.
- **"How would this scale to bigger files?"** → Summary generation itself is
  pandas, which scales fine. For very wide/tall data, I'd sample rows and
  chunk the correlation matrix rather than passing every column.

## Resume / LinkedIn bullet points

- Built an AI-powered data analysis tool (Streamlit + pandas + Claude API)
  that auto-generates insight reports and answers natural-language questions
  over uploaded datasets.
- Designed a "compute-then-explain" pipeline where pandas performs
  statistical analysis and an LLM translates results into plain-language
  business insights, reducing manual EDA time.
- Deployed a live demo accessible via public URL, with secrets management
  and environment-based configuration for local vs. production use.

## Tech stack

- **Streamlit** — UI, file upload, chat interface
- **pandas** — statistical computation (describe, correlations, nulls)
- **Anthropic Claude API** — insight generation and Q&A
- **python-dotenv** — local secrets management
