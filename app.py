from flask import Flask, jsonify, request
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from flask_cors import CORS
from serpapi import GoogleSearch
import matplotlib.pyplot as plt
import io
import base64
import requests
from bs4 import BeautifulSoup
import json
import re
from llama_cpp import Llama  # Import the Llama model

app = Flask(__name__)
CORS(app)

# Configurations
SERP_API_KEY = "e0a2a06f38728ac255d81297d87bf68d7f2b953ee988d01142a2a4d48f1f35ca"
model_path = "models/Meta-Llama-3-8B-Instruct-Q5_K_M.gguf"
llm = Llama(model_path=model_path, n_gpu_layers=-1, n_ctx=20000)

# Load JSON Data
def load_data(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    df = pd.DataFrame(data['sales'])
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    return df

# Perform Forecasting using XGBoost
def forecast_sales_xgboost(sales_data, periods=52):
    sales_data['lag1'] = sales_data['units_sold'].shift(1)
    sales_data.dropna(inplace=True)
    X = sales_data[['lag1']]
    y = sales_data['units_sold']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = xgb.XGBRegressor(objective='reg:squarederror', colsample_bytree=0.3, learning_rate=0.1,
                             max_depth=5, alpha=10, n_estimators=100)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    mse = mean_squared_error(y_test, preds)
    print(f"XGBoost Mean Squared Error: {mse}")

    forecast_input = pd.DataFrame({'lag1': [sales_data['units_sold'].iloc[-1]]})
    forecast = []
    for _ in range(periods):
        next_forecast = model.predict(forecast_input)[0]
        forecast.append(next_forecast)
        forecast_input = pd.DataFrame({'lag1': [next_forecast]})

    return pd.Series(forecast)

# Apply Seasonal Trends
def apply_seasonal_trends(forecast, seasonal_trends):
    return forecast * pd.Series(seasonal_trends * (len(forecast) // len(seasonal_trends) + 1))[:len(forecast)]

# Fetch Data Using SERP API
def fetch_search_results(query):
    params = {
        "q": query,
        "hl": "en",
        "gl": "us",
        "api_key": SERP_API_KEY
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    links = [result['link'] for result in results.get('organic_results', [])]

    body_text = ''
    for link in links:
        print(f"Fetching content from: {link}")
        content = fetch_content(link)

        if content:
            soup = BeautifulSoup(content, 'html.parser')
            for paragraph in soup.find_all('p'):
                body_text += paragraph.get_text() + '\n'
            if body_text and len(body_text) > 3000:
                return body_text.replace("\n", "---")
    return body_text.replace("\n", "---")

# Generate Product Data
def get_product_data(product_name):
    file_path = f"{product_name.lower()}_sales.json"
    sales_data = load_data(file_path)

    # Generate forecast using XGBoost
    forecast_xgboost = forecast_sales_xgboost(sales_data, periods=52)

    # Apply seasonal trends
    seasonal_trends = [1.05, 1.05, 1.00, 1.00, 0.95, 0.95]
    adjusted_forecast_xgboost = apply_seasonal_trends(forecast_xgboost, seasonal_trends)

    return {
        "historical": sales_data['units_sold'].tolist(),
        "forecasted_xgboost": adjusted_forecast_xgboost.round(2).tolist(),
        "seasonal_trends": seasonal_trends
    }

# Generate Summarized Report Using Local LLM
@app.route('/api/generate_report', methods=['POST'])
def generate_report():
    content = request.json.get('content', 'Generate a summary of the latest trends in the agrochemical industry.')
    prompt = content
    response = llm(prompt=prompt, temperature=0.5, max_tokens=150, echo=False)
    summary = response['choices'][0]['text'].strip()
    return jsonify({"summary": summary})

# Generate Time Series Trend Graph with Trend Scores
@app.route('/api/generate_trend_graph', methods=['POST'])
def generate_trend_graph():
    trend_data = {
        "weeks": list(range(1, 53)),
        "trend_scores": [x * 0.1 + 1 for x in range(52)]
    }

    fig, ax = plt.subplots()
    ax.plot(trend_data['weeks'], trend_data['trend_scores'], marker='o')

    ax.set(xlabel='Weeks', ylabel='Trend Score', title='Time Series Trend Graph')
    ax.grid()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)

    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()

    return jsonify({"trend_graph": img_base64})

# Example endpoint to get product forecast
@app.route('/api/forecast', methods=['GET'])
def get_forecast():
    product = request.args.get('product')
    product_data = get_product_data(product)

    if product_data:
        return jsonify(product_data)
    else:
        return jsonify({"error": "Product data not found"}), 404

# Suggest Trends Using Local LLM
@app.route('/api/suggest_trends', methods=['POST'])
def suggest_trends():
    data = request.json
    product_details = data.get('productDetails')

    prompt = (
        f"You are an expert in the agro-based industry. Suggest trend, market trend, seasonal trend, "
        f"and economic trend search texts for a product with the following details:\n"
        f"Description: {product_details['description']}\n"
        f"Type: {product_details['type']}\n"
        f"Unit of Measurement: {product_details['unit_of_measurement']}\n"
        f"Make the suggestions specific and focused on excavating trends useful for business purposes. "
        f"Provide 2-3 suggestions in a comma-separated flat structure."
    )

    response = llm(prompt=prompt, temperature=0.5, max_tokens=150, echo=False)
    suggested_trends = response['choices'][0]['text'].strip().split("\n")

    return jsonify({"suggested_trends": suggested_trends})

# Generate Trend Report Using Local LLM
def generate_trend_report(search_results):
    combined_text = " ".join([result.get('snippet', '') for result in search_results])

    prompt = (
        f"Based on the following data: {combined_text}, generate a detailed trend analysis report. "
        f"Please include clear, structured outputs for each trend, highlighting key trend scores "
        f"for specific weeks. Follow this format for clarity:\n\n"
        f"Week X: Trend Score Y\n"
        f"Week X: Trend Score Y\n..."
    )

    response = llm(prompt=prompt, temperature=0.5, max_tokens=150, echo=False)
    report_text = response['choices'][0]['text'].strip()

    return report_text

# Generate Structured Data for Plotting
def generate_structured_data_for_plotting(report_text):
    prompt = (
        f"Based on the following report: {report_text}, structure the data to create a plot with elements "
        f"for Week, Trend Score, and Trend Name. Provide the data in XML format."
    )

    response = llm(prompt=prompt, temperature=0.5, max_tokens=150, echo=False)
    xml_data = response['choices'][0]['text'].strip()

    return xml_data

# Fetch Content from a URL
def fetch_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch {url}: {e}")
        return None

# Scrape Website Data
def scrape_website_data(website_links):
    scraped_data = []
    headers = {'User-Agent': 'Mozilla/5.0'}

    for link in website_links:
        try:
            response = requests.get(link, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            paragraphs = [p.get_text() for p in soup.find_all('p')]
            scraped_data.extend(paragraphs)

        except Exception as e:
            print(f"Error scraping {link}: {e}")

    return ' '.join(scraped_data)

# Run Trend Analysis Using Local LLM
@app.route('/api/run_trend_analysis', methods=['POST'])
def run_trend_analysis():
    request_data = request.json
    trend_descriptions = request_data['trend_descriptions']
    website_links = request_data['website_links']
    customer_reviews = request_data['customer_reviews']

    all_search_results = []
    for trend in trend_descriptions:
        search_results = fetch_search_results(trend)
        all_search_results.extend(search_results)

    combined_data = ' '.join(trend_descriptions) + ' '.join([review['review'] for review in customer_reviews]) + str(all_search_results)

    prompt = (
        f"Generate a trend analysis report based on the following data for the last 6 months, considering the customer reviews. "
        f"Write a comprehensive report in a professional and easy-to-understand structure with headings and subheadings. "
        f"Please include statistics wherever necessary: {combined_data}. Follow a standard report template."
    )

    report = llm(prompt=prompt, temperature=0.5, max_tokens=150, echo=False)

    plot_prompt = f"Based on the following report: {report['choices'][0]['text'].strip()}, structure the data to create a plot with columns for Week, Trend Score, and Trend Name. Provide the data in JSON format."
    structured_response = llm(prompt=plot_prompt, temperature=0.5, max_tokens=150, echo=False)

    plotr = structured_response['choices'][0]['text'].strip()
    plotr = plotr.replace("json", "")
    pr = ""
    try:
        pr = eval(plotr)
    except:
        pass

    return jsonify({
        "report": report['choices'][0]['text'].strip(),
        "structured_data": pr
    })

if __name__ == '__main__':
    app.run(debug=True)
