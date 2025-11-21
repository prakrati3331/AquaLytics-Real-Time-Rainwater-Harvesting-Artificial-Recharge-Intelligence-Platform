# Integrated Water Resource Management System

A comprehensive web-based platform that combines **Rainwater Harvesting Analysis** and **Aquifer Type Prediction** to provide intelligent water resource management solutions for sustainable development.

## 🌟 Features

### 🌧️ Rainwater Harvesting Analysis
- **Location-based Analysis**: Get detailed rainwater harvesting feasibility for any district and state in India
- **Roof Type Optimization**: Supports different roof types (Concrete, GI Sheet, Tile, Thatched) with appropriate runoff coefficients
- **Water Demand Calculation**: Calculates annual water demand based on number of dwellers
- **Feasibility Scoring**: Provides comprehensive feasibility scores based on rainfall, runoff, groundwater levels, and aquifer characteristics
- **Interactive Maps**: Visual representation of rainfall patterns, groundwater levels, and aquifer distribution

### 🏔️ Aquifer Prediction System
- **ML-Powered Predictions**: Machine learning model to predict aquifer types based on geological and hydrological parameters
- **Real-time Analysis**: Instant prediction of aquifer characteristics using elevation, rainfall, and groundwater data
- **Probability Assessment**: Provides confidence scores for different aquifer type predictions
- **State-wise Coverage**: Supports all Indian states and union territories

### 🗺️ Interactive Visualizations
- **SVG-based Maps**: Color-coded maps showing rainfall distribution, groundwater levels, and aquifer types
- **Dynamic Highlighting**: Interactive district highlighting on maps
- **Multiple Time Periods**: Pre-monsoon, post-monsoon, and annual rainfall visualizations

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd SIH-65-main
   ```

2. **Create virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify installation**
   ```bash
   python -c "import fastapi, pandas, numpy, joblib, uvicorn; print('All dependencies installed successfully!')"
   ```

## 🎯 Usage

### Running the Application

**Start the integrated server:**
```bash
python integrated_app.py
```

The application will start on `http://localhost:8000` (or `http://127.0.0.1:8000`)

**Alternative: Using uvicorn directly**
```bash
uvicorn integrated_app:app --host 0.0.0.0 --port 8000 --reload
```

### Accessing the Application

1. **Main Interface**: Open `http://localhost:8000` in your browser
2. **Aquifer Interface**: Visit `http://localhost:8000/aquifer` for aquifer-specific analysis
3. **Advanced Analysis**: Go to `http://localhost:8000/aquifer-analysis` for detailed aquifer predictions

## 🔌 API Endpoints

### Rainwater Harvesting Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Main web interface |
| `POST` | `/process-location` | Analyze rainwater harvesting feasibility |
| `GET` | `/groundwater-trends` | Historical groundwater level trends |

### Aquifer Prediction Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/aquifer` | Aquifer prediction interface |
| `GET` | `/aquifer-analysis` | Advanced aquifer analysis interface |
| `GET` | `/aquifer/status` | API status and model information |
| `POST` | `/aquifer/predict` | Predict aquifer type |
| `GET` | `/aquifer/features` | Get model features |
| `GET` | `/aquifer/classes` | Get possible aquifer classes |

### System Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | System health check |

## 📊 Data Parameters

### Rainwater Harvesting Input
```json
{
  "district": "Mumbai",
  "state": "Maharashtra",
  "roofArea": 100.0,
  "roofType": "CONCRETE",
  "dwellers": 4
}
```

### Aquifer Prediction Input
```json
{
  "state": "Maharashtra",
  "district": "Mumbai",
  "pre_monsoon": "10-15",
  "post_monsoon": "5-8",
  "fluctuation": 5.2,
  "elevation": 14.0,
  "actual_rainfall": 2500.5,
  "normal_rainfall": 2300.8,
  "percent_dep": 8.9
}
```

## 📁 Project Structure

```
SIH-65-main/
├── 📄 Core Application Files
│   ├── integrated_app.py      # Main integrated application
│   ├── app.py                 # Rainwater harvesting module
│   ├── aquifier_main.py       # Aquifer prediction module
│   ├── rwh.py                 # Rainwater harvesting calculations
│   ├── file_handling.py       # Data processing utilities
│   └── SVGcoloring.py         # Map visualization functions
│
├── 📊 Data & Models
│   ├── aquifer_recommendation_model.pkl  # ML model
│   └── databases/                        # CSV databases
│       ├── rainfall_database.csv
│       ├── statewise_aquifier.csv
│       ├── aquifer_score.csv
│       └── groundwater*.csv (2019-2023)
│
├── 🖥️ Frontend
│   └── static/
│       ├── newindex.html           # Main interface
│       ├── aquifer_interface.html  # Aquifer interface
│       └── *.svg                   # Map visualizations
│
├── ⚙️ Configuration
│   ├── requirements.txt       # Python dependencies
│   ├── .gitignore           # Git ignore rules
│   └── README.md           # This file
│
└── 🧪 Testing & Utilities
    ├── test_integration.py  # Integration tests
    └── Various utility scripts
```

## 🛠️ Technologies Used

### Backend
- **FastAPI** - Modern, fast web framework for building APIs
- **Python** - Core programming language
- **Pandas** - Data manipulation and analysis
- **NumPy** - Numerical computing
- **Scikit-learn** - Machine learning algorithms
- **Joblib** - Model serialization

### Frontend
- **HTML5** - Semantic markup
- **CSS3** - Styling and responsive design
- **JavaScript** - Interactive functionality
- **SVG** - Scalable vector graphics for maps

### Data Processing
- **Pandas** - CSV data processing
- **Regular Expressions** - Data parsing and cleaning
- **Custom Algorithms** - Feasibility scoring and analysis

### Machine Learning
- **Scikit-learn** - Model training and prediction
- **Preprocessing** - Data normalization and encoding
- **Classification** - Aquifer type prediction

## 🎯 Use Cases

### For Individuals
- **Homeowners**: Determine rainwater harvesting feasibility
- **Farmers**: Understand local aquifer characteristics
- **Urban Planners**: Analyze water resource availability

### For Organizations
- **Government Agencies**: Water resource planning and management
- **Environmental NGOs**: Sustainability impact assessment
- **Research Institutions**: Hydrological studies and analysis
- **Water Management Companies**: Infrastructure planning

### For Developers
- **API Integration**: Embed water analysis in other applications
- **Data Analysis**: Use the datasets for further research
- **Model Enhancement**: Improve the ML models with additional data

## 🔧 Configuration

### Model Configuration
- Model file: `aquifer_recommendation_model.pkl`
- Features: Pre-monsoon levels, post-monsoon levels, elevation, rainfall data
- Target classes: Various aquifer types (Alluvial, Basaltic, etc.)

### Database Configuration
- Rainfall data: `databases/rainfall_database.csv`
- Aquifer data: `databases/statewise_aquifier.csv`
- Groundwater data: `databases/groundwater*.csv`

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**
4. **Add tests** if applicable
5. **Commit your changes**: `git commit -m 'Add amazing feature'`
6. **Push to the branch**: `git push origin feature/amazing-feature`
7. **Open a Pull Request**

### Areas for Contribution
- **Model Improvement**: Enhance the ML model accuracy
- **Additional Data Sources**: Integrate more hydrological data
- **UI/UX Enhancements**: Improve the web interface
- **API Documentation**: Expand API documentation
- **Testing**: Add comprehensive test coverage
- **Performance Optimization**: Improve application speed

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Smart India Hackathon (SIH)** for the inspiration and platform
- **Central Ground Water Board (CGWB)** for hydrological data
- **Indian Meteorological Department (IMD)** for rainfall data
- **Open Source Community** for the amazing tools and libraries

## 📞 Support

For support, please contact:
- **Email**: shubhammallick@gmail.com
- **Issues**: Create an issue in the GitHub repository
- **Discussions**: Use GitHub Discussions for questions and ideas

---

**Made with ❤️ for sustainable water resource management**

Download PPT
https://github.com/prakrati3331/AquaLytics-Real-Time-Rainwater-Harvesting-Artificial-Recharge-Intelligence-Platform/blob/main/RWHS%20PPT.pptx
