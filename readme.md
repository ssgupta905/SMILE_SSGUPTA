Product Details and Trend Analysis Web Application

Overview

This web application provides detailed product information along with trend analysis for a set of products. Users can view and edit product details, add new trend search texts, upload and analyze trends, and visualize trends with an interactive chart. The app allows users to scrape websites for trend-related information, analyze customer reviews, and generate a trend report with structured data visualizations.

Features

Product Selection and Details:
Allows users to select a product from a dropdown list and view/edit its details such as name, description, and trend search texts.
Users can add and remove trend search texts dynamically.
Trend Suggestion:
Suggests trends based on product details and the trend duration using an API (/api/suggest_trends).
Allows users to select suggested trends and add them to the product details.
Website Links for Data Scraping:
Users can add and manage website links that will be used for scraping trend-related data during trend analysis.
Customer Reviews:
Displays customer reviews and allows users to analyze them as part of the trend analysis.
Trend Analysis:
Users can run a detailed trend analysis, which includes the product's trend search texts, website links, and customer reviews, via an API (/api/run_trend_analysis).
The app generates a detailed trend report with key insights and structured data.
Trend Report and Download:
After the trend analysis, a detailed report is generated and displayed on the page.
Users can download the generated trend report as a .txt file.
Trend Plot:
A line chart visualizes the structured trend data over time, showing different trend scores for multiple trends. The chart is generated dynamically using Chart.js.
Loading Spinner:
A loading spinner is displayed when the app is waiting for a response from the backend during trend suggestion or trend analysis operations.
Collapsible Sections:
The UI uses collapsible sections for easy navigation of product details, trend search texts, website links, customer reviews, trend reports, and trend plots.
Frontend Technologies Used

React: For building the user interface and managing state with hooks (useState, useEffect, useRef).
React Router: For handling dynamic routing and navigation.
React Icons: For using icons such as FaDownload, FaLightbulb, FaChevronDown, etc.
Chart.js: For creating the trend score visualizations.
ClipLoader: For the loading spinner while waiting for data.
Modal: For displaying suggested trends in a popup dialog.
CSS: For custom styling of the UI.
Backend APIs

This application relies on the following backend APIs:

/api/suggest_trends:
Method: POST
Description: Suggests trends based on product details and the selected trend duration.
Request Body:
json
Copy code
{
  "productDetails": { /* Product details */ },
  "trendDuration": 6  // Number of months
}
Response:
json
Copy code
{
  "suggested_trends": ["trend1", "trend2", "trend3"]
}
/api/run_trend_analysis:
Method: POST
Description: Runs a trend analysis using product trend search texts, website links, and customer reviews.
Request Body:
json
Copy code
{
  "trend_descriptions": ["trend1", "trend2"],
  "website_links": ["link1", "link2"],
  "customer_reviews": [{ "review": "review text", "rating": 5 }]
}
Response:
json
Copy code
{
  "report": "Generated trend report",
  "structured_data": [
    { "Week": 1, "Trend Name": "Trend1", "Trend Score": 8 },
    { "Week": 2, "Trend Name": "Trend2", "Trend Score": 7 }
  ]
}
How to Set Up and Run the Application

Prerequisites
Before running this project, make sure you have the following installed:

Node.js: Ensure that Node.js is installed. If not, download it from Node.js website.
npm: The Node Package Manager (npm) comes with Node.js.
Installation Steps
Clone the repository:
bash
Copy code
git clone <repository-url>
Navigate to the project directory:
bash
Copy code
cd <project-directory>
Install dependencies: Run the following command to install the required npm packages:
bash
Copy code
npm install
Start the development server: After installation, start the React development server using:
bash
Copy code
npm start
The app will be available on http://localhost:3000.
Setting Up Backend
The backend for this project should be running to handle the requests made to /api/suggest_trends and /api/run_trend_analysis.

Ensure the backend server (e.g., a Python Flask or Node.js Express server) is running on http://localhost:5000.
Implement or mock the backend APIs according to the documentation above.
Building for Production
To create an optimized production build:

bash
Copy code
npm run build
The build artifacts will be located in the build/ folder. These can be served via a static file server or deployed to a hosting service such as Netlify or Vercel.

File Structure

plaintext
Copy code
|-- public/
|-- src/
|   |-- components/
|   |   |-- ProductDetails.js  // Main component for product details and trend analysis
|   |-- styles.css             // Custom styling for the application
|-- App.js                     // Main app entry point
|-- index.js                   // React DOM rendering
|-- package.json               // Project dependencies and scripts
Key Components

ProductDetails.js: The main component responsible for displaying product details and managing trend analysis. It contains the following key functionalities:
Product selection and details editing.
Adding/removing trend search texts and website links.
Triggering API requests for trend suggestions and trend analysis.
Displaying a modal for selecting suggested trends.
Visualizing trend data using a collapsible chart.
styles.css: Contains custom CSS styles for layout, collapsible sections, buttons, and loading spinner.
Deployment

To deploy the application:

Ensure that the frontend is built using npm run build.
Deploy the contents of the build folder to your preferred hosting provider (e.g., Netlify, Vercel, Heroku).
Ensure the backend APIs are hosted on a publicly accessible URL and update the API endpoints in the code if necessary.
Usage

Select a product from the dropdown to view and edit its details.
Add new trend search texts or select suggested trends using the suggestion feature.
Add website links for data scraping purposes.
Analyze trends by running the trend analysis, which will generate a report and plot trend scores over time.
Download the trend report for future reference.
Future Enhancements

User Authentication: Add login functionality to restrict access to the product details and trend analysis features.
Enhanced Trend Prediction: Implement machine learning models to predict future trends based on the historical data.
API Error Handling: Add more robust error handling for API requests and display user-friendly error messages.
By following this README, you should be able to set up, run, and explore the functionality of the Product Details and Trend Analysis web application.
