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

## Sample Data

The application uses a sample dataset to demonstrate its capabilities. The sample data is structured to include detailed information about a warehouse, its inventory, sales data, nearby inventories, and shippers. Below is a description of the key components of the sample data:

1. **Warehouse Information:**
   - Contains details about the warehouse, including its ID, name, and location.
   - Includes a list of materials in the warehouse inventory, each with attributes like material ID, name, quantity, unit, reorder level, supplier, batch number, last restock date, and next restock date.

2. **Sales Data:**
   - Historical sales data for each material over multiple years.
   - Each year's data is broken down by month, providing the quantity sold for each material.

3. **Nearby Inventories:**
   - Information about nearby warehouses and plants, including their location, distance from the central warehouse, and the inventory or production capacity for each material.
   - Each entry includes actual and forecasted quantities of materials delivered.

4. **Shippers:**
   - Details about the shippers used by the warehouse, including their reliability score, average delivery time, and cost per kilometer.

This structured sample data is used to drive various functionalities within the application, such as inventory management, trend analysis, and visualization of sales data.

## How to Set Up and Run the Application

### Prerequisites

Before running this project, make sure you have the following installed:

- **Node.js**: Ensure that Node.js is installed. If not, download it from [Node.js website](https://nodejs.org/).
- **npm**: The Node Package Manager (npm) comes with Node.js.

### Installation Steps

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
