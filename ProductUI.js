import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { FaDownload, FaLightbulb, FaChartLine, FaTrash, FaChevronDown, FaChevronUp, FaLink, FaPlus } from 'react-icons/fa';
import Modal from 'react-modal';
import Chart from 'chart.js/auto';
import ClipLoader from "react-spinners/ClipLoader";
import './styles.css';

Modal.setAppElement('#root');

function ProductDetails() {
    const { productId } = useParams();
    const [products, setProducts] = useState([]);
    const [selectedProduct, setSelectedProduct] = useState(null);
    const [productDetails, setProductDetails] = useState(null);
    const [suggestions, setSuggestions] = useState([]);
    const [newTrend, setNewTrend] = useState("");
    const [trendDuration, setTrendDuration] = useState(6);
    const [websiteLinks, setWebsiteLinks] = useState([]);  // State for website links
    const [newLink, setNewLink] = useState("");  // State for new website link
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [trendReport, setTrendReport] = useState("");
    const [structuredData, setStructuredData] = useState(null);
    const [isCollapsed, setIsCollapsed] = useState({
        description: false,
        trendTexts: false,
        trendReport: false,
        trendPlot: false,
        websiteLinks: false,  // For collapsing the website links section
        customerReviews: false  // For collapsing the customer reviews section
    });
    const [loading, setLoading] = useState(false);
    const chartRef = useRef(null);
    const chartInstance = useRef(null);
    const navigate = useNavigate();

    useEffect(() => {
        fetch('/product_details.json')
            .then(response => response.json())
            .then(data => {
                setProducts(data.products);
                const product = data.products.find(p => p.id === parseInt(productId));
                if (product) {
                    setSelectedProduct(product.id);
                    setProductDetails(product);
                } else {
                    console.error("Product not found");
                }
            })
            .catch(error => console.error("Error fetching product details:", error));
    }, [productId]);

    const handleProductChange = (event) => {
        const productId = event.target.value;
        const product = products.find(p => p.id === parseInt(productId));
        if (product) {
            setSelectedProduct(productId);
            setProductDetails(product);
            navigate(`/details/${productId}`);
        } else {
            console.error("Product not found");
        }
    };

    const handleDetailChange = (field, value) => {
        setProductDetails({
            ...productDetails,
            [field]: value
        });
    };

    const handleTrendTextChange = (index, value) => {
        const updatedTrends = [...productDetails.trend_descriptions];
        updatedTrends[index] = value;
        setProductDetails({
            ...productDetails,
            trend_descriptions: updatedTrends
        });
    };

    const addTrend = () => {
        if (newTrend.trim()) {
            setProductDetails({
                ...productDetails,
                trend_descriptions: [...productDetails.trend_descriptions, newTrend]
            });
            setNewTrend("");
        }
    };

    const deleteTrend = (index) => {
        const updatedTrends = [...productDetails.trend_descriptions];
        updatedTrends.splice(index, 1);
        setProductDetails({
            ...productDetails,
            trend_descriptions: updatedTrends
        });
    };

    const addLink = () => {
        if (newLink.trim()) {
            setWebsiteLinks([...websiteLinks, newLink]);
            setNewLink("");
        }
    };

    const deleteLink = (index) => {
        const updatedLinks = [...websiteLinks];
        updatedLinks.splice(index, 1);
        setWebsiteLinks(updatedLinks);
    };

    const handleSuggestTrends = async () => {
        setLoading(true);
        try {
            const response = await fetch('http://localhost:5000/api/suggest_trends', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ productDetails, trendDuration })
            });
            const data = await response.json();

            const cleanedSuggestions = data.suggested_trends[0]
                .replace(/(^"|"$)/g, '')  
                .split('", "')  
                .map(s => ({ text: s.replace(/[^a-zA-Z0-9\s.,]/g, '').trim(), selected: false }));

            setSuggestions(cleanedSuggestions);
            setIsModalOpen(true);
        } catch (error) {
            console.error("Error suggesting trends:", error);
        } finally {
            setLoading(false);
        }
    };

    const handleAddSuggestions = () => {
        const selectedSuggestions = suggestions.filter(s => s.selected).map(s => s.text);
        setProductDetails({
            ...productDetails,
            trend_descriptions: [...productDetails.trend_descriptions, ...selectedSuggestions]
        });
        setIsModalOpen(false);
    };

    const toggleSuggestionSelection = (index) => {
        const updatedSuggestions = suggestions.map((suggestion, i) => 
            i === index ? { ...suggestion, selected: !suggestion.selected } : suggestion
        );
        setSuggestions(updatedSuggestions);
    };

    const handleRunAnalysis = async () => {
        setLoading(true);
        try {
            const response = await fetch('http://localhost:5000/api/run_trend_analysis', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    trend_descriptions: productDetails.trend_descriptions,
                    website_links: websiteLinks,  // Include website links in the request
                    customer_reviews: productDetails.reviews // Include customer reviews in the request
                })
            });
            const data = await response.json();

            setTrendReport(data.report);
            if (Array.isArray(data.structured_data)) {
                setStructuredData(data.structured_data);
            } else {
                console.error("structuredData is not an array:", data.structured_data);
            }
        } catch (error) {
            console.error("Error running trend analysis:", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (structuredData && Array.isArray(structuredData) && chartRef.current) {
            if (chartInstance.current) {
                chartInstance.current.destroy();
            }

            const groupedData = structuredData.reduce((acc, item) => {
                if (!acc[item["Trend Name"]]) {
                    acc[item["Trend Name"]] = [];
                }
                acc[item["Trend Name"]].push({ week: item.Week, score: item["Trend Score"] });
                return acc;
            }, {});

            const trendNames = Object.keys(groupedData);
            const weeks = [...new Set(structuredData.map(item => item.Week))].sort((a, b) => a - b);

            const datasets = trendNames.map(name => {
                const data = weeks.map(week => {
                    const entry = groupedData[name].find(item => item.week === week);
                    return entry ? entry.score : null;
                });
                return {
                    label: name,
                    data,
                    borderColor: getRandomColor(),
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    fill: true,
                };
            });

            const ctx = chartRef.current.getContext('2d');
            chartInstance.current = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: weeks,
                    datasets: datasets,
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: {
                            type: 'category',
                            title: {
                                display: true,
                                text: 'Weeks'
                            }
                        },
                        y: {
                            type: 'linear',
                            title: {
                                display: true,
                                text: 'Trend Score'
                            }
                        }
                    }
                }
            });
        }
    }, [structuredData]);

    const getRandomColor = () => {
        const letters = '0123456789ABCDEF';
        let color = '#';
        for (let i = 0; i < 6; i++) {
            color += letters[Math.floor(Math.random() * 16)];
        }
        return color;
    };

    const parseReport = (report) => {
        const lines = report.split('\n');
        return lines.map((line, index) => {
            if (line.startsWith('## ')) {
                return <h2 key={index}>{line.replace('## ', '')}</h2>;
            } else if (line.startsWith('**')) {
                return <h3 key={index}>{line.replace(/\*\*/g, '')}</h3>;
            } else if (line.startsWith('* ')) {
                return <li key={index}>{line.replace('* ', '')}</li>;
            } else {
                return <p key={index}>{line}</p>;
            }
        });
    };

    const toggleCollapse = (section) => {
        setIsCollapsed(prevState => ({
            ...prevState,
            [section]: !prevState[section]
        }));
    };

    return (
        <div className="container">
            <h1>Product Details and Trend Analysis</h1>
            {loading && (
                <div className="spinner-overlay">
                    <ClipLoader color={"#123abc"} loading={loading} size={50} />
                </div>
            )}
            <div className={`content ${loading ? 'content-blur' : ''}`}>
                <div className="select-product">
                    <label htmlFor="product">Select Product:</label>
                    <select 
                        id="product" 
                        value={selectedProduct || ''} 
                        onChange={handleProductChange}
                    >
                        <option value="">--Select a Product--</option>
                        {products.map(product => (
                            <option key={product.id} value={product.id}>
                                {product.name}
                            </option>
                        ))}
                    </select>
                </div>
                
                {productDetails ? (
                    <div className="product-details">
                        <h2>
                            <input
                                type="text"
                                value={productDetails.name}
                                onChange={(e) => handleDetailChange('name', e.target.value)}
                            />
                        </h2>
                        
                        <div className="collapsible-section">
                            <div className="collapsible-header" onClick={() => toggleCollapse('description')}>
                                <strong>Description</strong>
                                {isCollapsed.description ? <FaChevronUp /> : <FaChevronDown />}
                            </div>
                            {!isCollapsed.description && (
                                <textarea
                                    value={productDetails.description}
                                    onChange={(e) => handleDetailChange('description', e.target.value)}
                                />
                            )}
                        </div>

                        <div className="collapsible-section">
                            <div className="collapsible-header" onClick={() => toggleCollapse('trendTexts')}>
                                <strong>Trend Search Texts</strong>
                                {isCollapsed.trendTexts ? <FaChevronUp /> : <FaChevronDown />}
                            </div>
                            {!isCollapsed.trendTexts && (
                                <ul>
                                    {productDetails.trend_descriptions.map((description, index) => (
                                        <li key={index}>
                                            <input
                                                type="text"
                                                value={description}
                                                onChange={(e) => handleTrendTextChange(index, e.target.value)}
                                            />
                                            <button className="button icon-button" onClick={() => deleteTrend(index)}>
                                                <FaTrash />
                                            </button>
                                        </li>
                                    ))}
                                </ul>
                            )}
                            <div className="new-trend">
                                <input
                                    type="text"
                                    placeholder="Add new trend search text"
                                    value={newTrend}
                                    onChange={(e) => setNewTrend(e.target.value)}
                                />
                                <button className="button" onClick={addTrend}>+</button>
                                <button className="button icon-button" onClick={handleSuggestTrends}>
                                    <FaLightbulb />
                                </button>
                            </div>
                            <div className="duration-field">
                                <label htmlFor="duration">Trend Duration (Months):</label>
                                <input
                                    type="number"
                                    id="duration"
                                    value={trendDuration}
                                    onChange={(e) => setTrendDuration(e.target.value)}
                                    min="1"
                                />
                            </div>
                        </div>

                        <div className="collapsible-section">
                            <div className="collapsible-header" onClick={() => toggleCollapse('websiteLinks')}>
                                <strong>Website Links for Data Scraping</strong> <FaLink />
                                {isCollapsed.websiteLinks ? <FaChevronUp /> : <FaChevronDown />}
                            </div>
                            {!isCollapsed.websiteLinks && (
                                <>
                                    <ul>
                                        {websiteLinks.map((link, index) => (
                                            <li key={index}>
                                                <a href={link} target="_blank" rel="noopener noreferrer">{link}</a>
                                                <button className="button icon-button" onClick={() => deleteLink(index)}>
                                                    <FaTrash />
                                                </button>
                                            </li>
                                        ))}
                                    </ul>
                                    <div className="new-link">
                                        <input
                                            type="text"
                                            placeholder="Add new website link"
                                            value={newLink}
                                            onChange={(e) => setNewLink(e.target.value)}
                                        />
                                        <button className="button" onClick={addLink}><FaPlus /></button>
                                    </div>
                                </>
                            )}
                        </div>

                        <div className="collapsible-section">
                            <div className="collapsible-header" onClick={() => toggleCollapse('customerReviews')}>
                                <strong>Customer Reviews</strong> <FaChevronDown />
                                {isCollapsed.customerReviews ? <FaChevronUp /> : <FaChevronDown />}
                            </div>
                            {!isCollapsed.customerReviews && (
                                <ul>
                                    {productDetails.reviews.map((review, index) => (
                                        <li key={index}>
                                            <strong>{review.customer_name}</strong>: {review.review} ({review.rating} stars)
                                        </li>
                                    ))}
                                </ul>
                            )}
                        </div>

                        <button className="button run-analysis-button" onClick={handleRunAnalysis}>Run Trend Analysis</button>

                        <div className="collapsible-section">
                            <div className="collapsible-header" onClick={() => toggleCollapse('trendReport')}>
                                <strong>Generated Trend Report</strong> <FaDownload />
                                {isCollapsed.trendReport ? <FaChevronUp /> : <FaChevronDown />}
                            </div>
                            {!isCollapsed.trendReport && trendReport && (
                                <div className="trend-report">
                                    <div className="parsed-report">
                                        {parseReport(trendReport)}
                                    </div>
                                    <a href={`data:text/plain;charset=utf-8,${encodeURIComponent(trendReport)}`} download="Trend_Report.txt">
                                        <button className="button download-button"><FaDownload /> Download Report</button>
                                    </a>
                                </div>
                            )}
                        </div>

                        <div className="collapsible-section">
                            <div className="collapsible-header" onClick={() => toggleCollapse('trendPlot')}>
                                <strong>Trend Plot</strong> <FaChartLine />
                                {isCollapsed.trendPlot ? <FaChevronUp /> : <FaChevronDown />}
                            </div>
                            {!isCollapsed.trendPlot && structuredData && (
                                <div className="trend-plot">
                                    <div className="chart-container">
                                        <canvas id="trendChart" ref={chartRef}></canvas>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                ) : (
                    <p>Loading product details...</p>
                )}

                <Modal
                    isOpen={isModalOpen}
                    onRequestClose={() => setIsModalOpen(false)}
                    contentLabel="Trend Suggestions"
                    className="modal"
                    overlayClassName="modal-overlay"
                >
                    <h2>Trend Suggestions</h2>
                    <div className="suggestions-container">
                        {suggestions.map((suggestion, index) => (
                            <span 
                                key={index} 
                                className={`pill ${suggestion.selected ? 'selected' : ''}`}
                                onClick={() => toggleSuggestionSelection(index)}
                            >
                                {suggestion.text}
                            </span>
                        ))}
                    </div>
                    <button className="button" onClick={handleAddSuggestions}>Add Selected Suggestions</button>
                    <button className="button" onClick={() => setIsModalOpen(false)}>Close</button>
                </Modal>
            </div>
        </div>
    );
}

export default ProductDetails;
