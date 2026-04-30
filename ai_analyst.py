import os
from google import genai
import polars as pl
from openai import OpenAI

# Native .env parser to avoid external dependencies
if os.path.exists(".env"):
    with open(".env", "r") as _f:
        for _line in _f:
            if '=' in _line and not _line.strip().startswith('#'):
                _k, _v = _line.strip().split('=', 1)
                os.environ.setdefault(_k.strip(), _v.strip())

_api_key = os.getenv("GEMINI_API_KEY")
_groq_key = os.getenv("GROQ_API_KEY")
_client = None

def _get_client():
    global _client
    if _client is None:
        if not _api_key:
            return None
        _client = genai.Client(api_key=_api_key)
    return _client

# Priority list for Gemini models
GEMINI_MODELS = ["gemini-2.5-flash", "gemini-2.5-flash-lite"]

def _generate_with_fallback(prompt: str) -> str:
    """Attempts generation with Gemini models first, then falls back to Groq."""
    client = _get_client()
    last_error = None
    
    # 1. Try Gemini Models
    if client:
        for model_id in GEMINI_MODELS:
            try:
                response = client.models.generate_content(model=model_id, contents=prompt)
                return response.text
            except Exception as e:
                last_error = e
                continue
    
    # 2. Try Groq Fallback (as requested by user)
    if _groq_key:
        try:
            groq_client = OpenAI(
                api_key=_groq_key,
                base_url="https://api.groq.com/openai/v1",
            )
            completion = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )
            return completion.choices[0].message.content
        except Exception as e:
            last_error = f"Gemini failed, and Groq failed: {e}"
            
    if not _api_key and not _groq_key:
        return "_No API keys configured. Please add GEMINI_API_KEY or GROQ_API_KEY to your .env file._"
        
    return f"_All AI providers failed. Last error: {last_error}_"

def generate_comparison_report(country_a: str, country_b: str, stats_a: dict, stats_b: dict) -> str:
    """Generates an editorial-style comparative analysis between two countries."""
    prompt = f"""You are a senior research analyst for a global religion and sociology think tank.
Write a high-end, editorial-style comparative analysis (250 words max) between {country_a} and {country_b} based strictly on the following data.
Do NOT invent numbers. Use only the statistics provided.

--- {country_a} (Historical Peak: {stats_a.get('peak_shift_decade', 'N/A')}s) ---
- Dominant religion across the period: {stats_a.get('dominant_religion', 'N/A')}
- Fastest growing religion: {stats_a.get('fastest_growing', 'N/A')} (+{stats_a.get('fastest_growing_delta', '?')}pp)
- Steepest decline: {stats_a.get('fastest_declining', 'N/A')} ({stats_a.get('fastest_declining_delta', '?')}pp)
- Unaffiliated share in latest year: {stats_a.get('unaffiliated_latest', '?')}%

--- {country_b} (Historical Peak: {stats_b.get('peak_shift_decade', 'N/A')}s) ---
- Dominant religion across the period: {stats_b.get('dominant_religion', 'N/A')}
- Fastest growing religion: {stats_b.get('fastest_growing', 'N/A')} (+{stats_b.get('fastest_growing_delta', '?')}pp)
- Steepest decline: {stats_b.get('fastest_declining', 'N/A')} ({stats_b.get('fastest_declining_delta', '?')}pp)
- Unaffiliated share in latest year: {stats_b.get('unaffiliated_latest', '?')}%

Write in a structured, architectural tone. Highlight structural similarities and divergences.
How do their different historical peaks influence their current religious composition?
End with one sentence on what this contrast reveals about global religious trends."""
    return _generate_with_fallback(prompt)

def generate_impact_analysis(country: str, year_start: int, year_end: int, stats: dict) -> str:
    """Generates a socioeconomic impact analysis for a single country's religious shifts."""
    prompt = f"""You are an interdisciplinary research analyst combining sociology, economics, and religious studies.

Analyse how the structural religious shifts in {country} between {year_start} and {year_end} may correlate with socioeconomic outcomes.
Use the data below as your factual anchor. Do NOT invent specific statistics for unemployment or crime — instead, reason from historical knowledge of how religious demographic shifts have correlated with these indicators globally and in this specific country.

--- {country} Religious Data ({year_start}–{year_end}) ---
- Historical Tipping Point: {stats.get('peak_shift_decade', 'N/A')}s (Use this for long-term context)
- Dominant religion: {stats.get('dominant_religion', 'N/A')}
- Fastest growing: {stats.get('fastest_growing', 'N/A')} (+{stats.get('fastest_growing_delta', '?')}pp)
- Steepest decline: {stats.get('fastest_declining', 'N/A')} ({stats.get('fastest_declining_delta', '?')}pp)
- Unaffiliated share today: {stats.get('unaffiliated_latest', '?')}%

Write a structured analytical report (300 words max) with these sections:
1. **Overview of the Shift** — summarize the religious transformation.
2. **Labor Market & Employment** — correlations with labor force participation, occupational patterns, or migration.
3. **Crime & Social Cohesion** — correlations between religious composition changes and social stability.
4. **Inflation & Economic Cycles** — how religiosity influenced saving behaviour, consumption, or institutional trust.
5. **Key Takeaway** — one sentence synthesis.

Be analytical, not ideological. Acknowledge where correlation does not imply causation."""
    return _generate_with_fallback(prompt)

def generate_comparative_impact_analysis(country_a: str, country_b: str, year_start: int, year_end: int, stats_a: dict, stats_b: dict) -> str:
    """Generates a comparative socioeconomic impact report between two countries."""
    prompt = f"""You are a senior interdisciplinary analyst comparing {country_a} and {country_b}.

Provide a comparative socioeconomic analysis (350 words max) based on their religious shifts between {year_start} and {year_end}.
Contrast how their different religious trajectories (secularization, growth of specific faiths) correlate with their divergent or similar economic paths.

--- Data for {country_a} ---
- Tipping Point: {stats_a.get('peak_shift_decade', 'N/A')}s
- Main Religions: {stats_a.get('dominant_religion', 'N/A')}
- Growth/Decline: {stats_a.get('fastest_growing', 'N/A')} (+{stats_a.get('fastest_growing_delta', '?')}pp) vs {stats_a.get('fastest_declining', 'N/A')}

--- Data for {country_b} ---
- Tipping Point: {stats_b.get('peak_shift_decade', 'N/A')}s
- Main Religions: {stats_b.get('dominant_religion', 'N/A')}
- Growth/Decline: {stats_b.get('fastest_growing', 'N/A')} (+{stats_b.get('fastest_growing_delta', '?')}pp) vs {stats_b.get('fastest_declining', 'N/A')}

Focus on:
1. **Divergent Paths** — how do their different religious shifts create different labor or social pressures?
2. **Economic Resilience** — which model shows higher correlation with institutional stability or labor flexibility?
3. **Social Cohesion** — compare the crime and cohesion metrics based on religious shifts.
4. **Synthesis** — final takeaway on the 'Religion-Economy' nexus in these two contexts.

Be objective and architectural in tone."""
    return _generate_with_fallback(prompt)

def extract_country_stats(df_pandas, country: str) -> dict:
    """Extracts key stats for a given country from the filtered DataFrame."""
    country_df = df_pandas[df_pandas['country_name'] == country]
    if country_df.empty:
        return {}

    avg_share = country_df.groupby('religion_name')['percentage'].mean()
    dominant = avg_share.idxmax()

    first_year = country_df['year'].min()
    last_year = country_df['year'].max()

    first = country_df[country_df['year'] == first_year].set_index('religion_name')['percentage']
    last = country_df[country_df['year'] == last_year].set_index('religion_name')['percentage']
    delta = (last - first).dropna()

    fastest_growing = delta.idxmax() if not delta.empty else 'N/A'
    fastest_growing_delta = round(delta.max(), 1) if not delta.empty else '?'
    fastest_declining = delta.idxmin() if not delta.empty else 'N/A'
    fastest_declining_delta = round(delta.min(), 1) if not delta.empty else '?'

    unaffiliated_row = country_df[(country_df['year'] == last_year) & (country_df['religion_name'] == 'Unaffiliated')]
    unaffiliated_latest = round(unaffiliated_row['percentage'].values[0], 1) if not unaffiliated_row.empty else '?'

    country_df = country_df.copy()
    country_df['decade'] = (country_df['year'] // 10) * 10
    volatility = country_df.groupby('decade')['percentage'].std().fillna(0)
    peak_decade = int(volatility.idxmax()) if not volatility.empty else 'N/A'

    return {
        'dominant_religion': dominant,
        'fastest_growing': fastest_growing,
        'fastest_growing_delta': fastest_growing_delta,
        'fastest_declining': fastest_declining,
        'fastest_declining_delta': fastest_declining_delta,
        'unaffiliated_latest': unaffiliated_latest,
        'peak_shift_decade': peak_decade
    }
