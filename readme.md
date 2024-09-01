# Product Details and Trend Analysis Web Application

## Overview

This web application provides detailed product information along with trend analysis for a set of products. Users can view and edit product details, add new trend search texts, upload and analyze trends, and visualize trends with an interactive chart. The app allows users to scrape websites for trend-related information, analyze customer reviews, and generate a trend report with structured data visualizations.

## Features

- **Product Selection and Details:**
  - Select a product from a dropdown list and view/edit its details such as name, description, and trend search texts.
  - Dynamically add and remove trend search texts.

- **Trend Suggestion:**
  - Suggest trends based on product details and the trend duration using an API (`/api/suggest_trends`).
  - Select suggested trends and add them to the product details.

- **Website Links for Data Scraping:**
  - Add and manage website links that will be used for scraping trend-related data during trend analysis.

- **Customer Reviews:**
  - Display customer reviews and include them in the trend analysis.

- **Trend Analysis:**
  - Run a detailed trend analysis, including the product's trend search texts, website links, and customer reviews, via an API (`/api/run_trend_analysis`).
  - Generate a detailed trend report with key insights and structured data.

- **Trend Report and Download:**
  - Display the generated trend report on the page.
  - Download the trend report as a `.txt` file.

- **Trend Plot:**
  - Visualize structured trend data over time using a line chart created with `Chart.js`.

- **Loading Spinner:**
  - Display a loading spinner while waiting for data from the backend during trend suggestion or trend analysis operations.

- **Collapsible Sections:**
  - Navigate product details, trend search texts, website links, customer reviews, trend reports, and trend plots using collapsible sections.

## Frontend Technologies Used

- **React**: For building the user interface and managing state with hooks (`useState`, `useEffect`, `useRef`).
- **React Router**: For handling dynamic routing and navigation.
- **React Icons**: For using icons such as `FaDownload`, `FaLightbulb`, `FaChevronDown`, etc.
- **Chart.js**: For creating the trend score visualizations.
- **ClipLoader**: For the loading spinner while waiting for data.
- **Modal**: For displaying suggested trends in a popup dialog.
- **CSS**: For custom styling of the UI.

## Backend APIs

This application relies on the following backend APIs:

1. **`/api/suggest_trends`**:
   - **Method**: `POST`
   - **Description**: Suggests trends based on product details and the selected trend duration.
   - **Request Body**:
     ```json
     {
       "productDetails": { /* Product details */ },
       "trendDuration": 6  // Number of months
     }
     ```
   - **Response**:
     ```json
     {
       "suggested_trends": ["trend1", "trend2", "trend3"]
     }
     ```

2. **`/api/run_trend_analysis`**:
   - **Method**: `POST`
   - **Description**: Runs a trend analysis using product trend search texts, website links, and customer reviews.
   - **Request Body**:
     ```json
     {
       "trend_descriptions": ["trend1", "trend2"],
       "website_links": ["link1", "link2"],
       "customer_reviews": [{ "review": "review text", "rating": 5 }]
     }
     ```
   - **Response**:
     ```json
     {
       "report": "Generated trend report",
       "structured_data": [
         { "Week": 1, "Trend Name": "Trend1", "Trend Score": 8 },
         { "Week": 2, "Trend Name": "Trend2", "Trend Score": 7 }
       ]
     }
     ```

## How to Set Up and Run the Application

### Prerequisites

Before running this project, make sure you have the following installed:

- **Node.js**: Ensure that Node.js is installed. If not, download it from [Node.js website](https://nodejs.org/).
- **npm**: The Node Package Manager (npm) comes with Node.js.

### Installation Steps

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
