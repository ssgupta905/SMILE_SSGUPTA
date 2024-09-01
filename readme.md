
# SMILE - SSGUPTA

## Overview

This repository contains a web application that integrates React for frontend and Python for backend services. The application is designed for managing product details, analyzing trends, and interacting with a backend service that uses quantized LLaMA 3 models for advanced trend analysis and forecasting. This README provides detailed steps to set up the entire project, including both the frontend and backend components.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

- **Node.js** (version 14.x or later)
- **npm** (Node Package Manager, comes with Node.js)
- **Python 3.8+**
- **Pip** (Python Package Manager)

## Getting Started

### Step 1: Clone the Repository

Start by cloning this repository to your local machine:

\`\`\`bash
git clone https://github.com/ssgupta905/SMILE_SSGUPTA.git
cd SMILE_SSGUPTA
\`\`\`

This will download the project files to a directory named `SMILE_SSGUPTA` and navigate into it.

### Step 2: Setting Up the Backend

The backend of this project utilizes Python with quantized LLaMA 3 models for trend analysis and forecasting. Here's how to set it up:

1. **Create a Virtual Environment:**

   It's recommended to create a Python virtual environment to manage dependencies:

   \`\`\`bash
   python -m venv venv
   source venv/bin/activate  # On Windows use \`venv\Scripts\activate\`
   \`\`\`

2. **Install Python Dependencies:**

   Install the necessary Python packages using \`pip\`:

   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`

   Ensure that \`requirements.txt\` includes dependencies like \`transformers\`, \`torch\`, \`dash\`, \`dash-bootstrap-components\`, \`pandas\`, \`neuralprophet\`, and others.

3. **Download and Configure LLaMA 3 Quantized Models:**

   Download the quantized LLaMA 3 models and place them in the \`models/\` directory. The backend code expects the model path to be something like \`models/Meta-Llama-3-8B-Instruct-Q5_K_M.gguf\`.

   \`\`\`bash
   mkdir -p models
   # Download your quantized LLaMA model here and place it in the models/ directory
   \`\`\`

4. **Load Sample Data:**

   Ensure that the sample data (\`warehouse_inventory.json\`) is located in the project root or a data directory. This JSON file contains the data structure required for the application.

5. **Run the Backend:**

   Start the backend server:

   \`\`\`bash
   python app.py
   \`\`\`

   This should start the Flask/Dash server on \`http://localhost:8050\`.

### Step 3: Setting Up the Frontend

The frontend is a React application that interacts with the Python backend. Here’s how to set it up:

1. **Install Create React App:**

   If you haven't already, install \`Create React App\` to set up a new React project with a standard configuration:

   \`\`\`bash
   npx create-react-app smile-ssgupta
   \`\`\`

2. **Navigate to the Project Directory:**

   Move to the newly created React app directory:

   \`\`\`bash
   cd smile-ssgupta
   \`\`\`

3. **Copy the \`ProductDetails.js\` File:**

   Copy the \`ProductDetails.js\` file from this repository to the \`src/components/\` directory of your React app:

   \`\`\`bash
   cp ../SMILE_SSGUPTA/ProductDetails.js src/components/
   \`\`\`

   Ensure that your React app has the \`components/\` directory in \`src/\`.

4. **Install Additional Dependencies:**

   Install the necessary React dependencies:

   \`\`\`bash
   npm install react-router-dom react-icons chart.js react-modal react-spinners
   \`\`\`

5. **Optional: Install Bootstrap for Styling:**

   If you want to use Bootstrap for styling, install \`react-bootstrap\` and \`bootstrap\`:

   \`\`\`bash
   npm install react-bootstrap bootstrap
   \`\`\`

   Add Bootstrap CSS to your \`index.js\` or \`App.js\` file:

   \`\`\`javascript
   import 'bootstrap/dist/css/bootstrap.min.css';
   \`\`\`

6. **Modify \`App.js\` to Include \`ProductDetails.js\`:**

   Update your \`App.js\` file to include the \`ProductDetails\` component and configure routing using \`react-router-dom\`.

   Example \`App.js\`:

   \`\`\`javascript
   import React from 'react';
   import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
   import ProductDetails from './components/ProductDetails';

   function App() {
       return (
           <Router>
               <Routes>
                   <Route path="/details/:productId" element={<ProductDetails />} />
                   {/* Add more routes as needed */}
               </Routes>
           </Router>
       );
   }

   export default App;
   \`\`\`

### Step 4: Running the Frontend

Start the React development server:

\`\`\`bash
npm start
\`\`\`

This will start the React application on \`http://localhost:3000\`.

### Step 5: Accessing the Application

With both the backend and frontend running, you can now interact with the application. Open your web browser and navigate to:

- **Frontend:** \`http://localhost:3000\`
- **Backend (API endpoints):** \`http://localhost:8050\`

### Using the Application

1. **Product Management:**
   - Select a product from the dropdown menu to view and edit its details.
   - Add, edit, or delete trend search texts and website links related to the product.

2. **Trend Analysis:**
   - Upload trend reports and integrate them with sales data for advanced forecasting.
   - Use the scenario simulation feature to generate and analyze potential scenarios that could impact warehouse operations.

3. **Visualizations:**
   - View various visualizations such as inventory levels, sales trends, and shipper reliability.
   - Interact with the dashboard's collapsible sections for better navigation.

### Future Enhancements

- **Advanced Authentication:** Implement user authentication to secure access to the dashboard.
- **Enhanced Analytics:** Introduce more advanced machine learning models for better predictions.
- **Expanded Visualizations:** Add more detailed and customizable data visualization options.

## Contributing

If you'd like to contribute to this project, please fork the repository and use a feature branch. Pull requests are welcome.

## License

This project is licensed under the MIT License.

---

By following this README, you should be able to set up, run, and explore the functionalities of the SMILE - SSGUPTA web application.
