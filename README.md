# Realtyvest AVM

**Automated Valuation Model for Dallas-Fort Worth Real Estate Market**

🚧 **Work in Progress** - Building an open-source alternative to Zillow's Zestimate

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![LightGBM](https://img.shields.io/badge/ML-LightGBM-green)](https://lightgbm.readthedocs.io/)
[![Status](https://img.shields.io/badge/Status-Alpha-yellow)](https://github.com/csperera/realtyvest-avm)

## 🎯 Project Goal

Built a production-grade Automated Valuation Model that achieves **<5% Median Absolute Error** on DFW residential properties, beating Zillow's ~7% benchmark.

## 🏗️ Architecture
```
Data Pipeline → Feature Engineering → ML Model → Predictions    
     ↓                ↓                   ↓            ↓        
  Scraper         Spatial           LightGBM      Dashboard     
  (Redfin)        Temporal          XGBoost       (Streamlit)    
                  Economic                                      
```

## 📊 Current Status

**Phase 1: Foundation** ✅
- [x] Modular project architecture
- [x] Web scraping pipeline (Redfin)
- [x] Data validation & cleaning
- [x] Configuration management

**Phase 2: Machine Learning** 🚧 In Progress
- [ ] Feature engineering pipeline
- [ ] LightGBM baseline model
- [ ] Walk-forward validation framework
- [ ] Hyperparameter optimization

**Phase 3: Production** 📅 Planned
- [ ] REST API (FastAPI)
- [ ] Interactive dashboard
- [ ] Automated monthly predictions
- [ ] Public accuracy leaderboard

## 🛠️ Tech Stack

**Data & ML:**
- Python 3.9+
- pandas, NumPy
- LightGBM, XGBoost
- scikit-learn

**Web & API:**
- BeautifulSoup4 (scraping)
- Streamlit (visualization)
- FastAPI (future API)

**Infrastructure:**
- PostgreSQL (planned)
- Docker (planned)

## 📂 Project Structure

```
realtyvest-avm/
├── config/              # Configuration files
│   ├── config.yaml
│   └── dfw_zips.yaml   # 175+ DFW ZIP codes
├── src/
│   ├── data/           # Data acquisition
│   │   └── scrapers/
│   ├── features/       # Feature engineering
│   ├── models/         # ML models
│   └── utils/          # Helper functions
├── notebooks/          # Exploration
└── tests/              # Unit tests
```


## 🚀 Quick Start

### Clone the repo
git clone https://github.com/csperera/realtyvest-avm.git
cd realtyvest-avm

### Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

### Install dependencies
pip install -r requirements.txt

## 🎓 Methodology

### Walk-Forward Validation
- Train on historical data only
- Predict current listings
- Score on actual closed sales
- **No future data leakage**

### Feature Categories
1. **Property**: beds, baths, sqft, age, lot size
2. **Spatial**: distance to amenities, school ratings
3. **Temporal**: seasonality, market trends
4. **Economic**: employment growth, population growth

## 📈 Target Metrics

| Metric | Target | Zillow Benchmark |
|--------|--------|------------------|
| MedAE  | <5%    | ~7%              |
| Coverage | 95%+ | ~90%            |
| Latency | <100ms | N/A            |

## 🤝 Contributing

This is a personal learning project, but suggestions and feedback are welcome!

## 📜 License

MIT License - See LICENSE file

## 👤 Author

**Christian Perera**
- Real estate investor with 30+ years experience
- Building tools to democratize property analysis

---

*Note: This is an educational project. Always consult licensed professionals for real estate investment decisions.*
