# MLOps Testing & CI/CD Pipeline Documentation

## 📋 Overview

This document describes the comprehensive testing framework and CI/CD pipelines for the Heart Disease Prediction ML system.

---

## 🧪 Testing Framework

### Unit Tests

The project includes extensive unit tests covering:

#### 1. **Data Processing Tests** (`tests/test_data_processing.py`)

**TestDataLoading**
- `test_load_csv()` - Validates CSV loading functionality
- `test_data_shape()` - Checks data dimensions and null values
- `test_target_column_exists()` - Ensures target column presence

**TestDataPreprocessing**
- `test_missing_value_handling()` - Tests imputation strategies
- `test_feature_scaling()` - Validates StandardScaler functionality
- `test_categorical_encoding()` - Tests OneHotEncoder

**TestDataValidation**
- `test_age_range()` - Validates age is within realistic bounds
- `test_binary_features()` - Checks binary features are 0 or 1
- `test_categorical_ranges()` - Validates feature value ranges
- `test_target_binary()` - Ensures target is binary classification

**TestDataSplitting**
- `test_train_test_split()` - Validates split functionality
- `test_stratified_split()` - Ensures class distribution preservation

#### 2. **Model Tests** (`tests/test_model.py`)

**TestModelCreation**
- `test_random_forest_creation()` - Tests model instantiation
- `test_preprocessing_pipeline()` - Validates preprocessing pipeline
- `test_full_pipeline_creation()` - Tests complete ML pipeline

**TestModelTraining**
- `test_model_training()` - Tests basic model fitting
- `test_pipeline_training()` - Tests full pipeline training
- `test_model_convergence()` - Ensures model learns from data

**TestModelPrediction**
- `test_predict_shape()` - Validates prediction output shape
- `test_predict_proba_shape()` - Validates probability output
- `test_predict_proba_valid()` - Ensures probabilities are in [0, 1]

**TestModelEvaluation**
- `test_accuracy_metric()` - Validates accuracy calculation
- `test_precision_recall_f1()` - Tests classification metrics
- `test_roc_auc()` - Validates ROC-AUC calculation

**TestModelPersistence**
- `test_model_save_and_load()` - Tests joblib serialization
- `test_loaded_model_prediction()` - Ensures loaded model works

### Running Tests Locally

```bash
# Install dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=src --cov=deployment/app --cov-report=html

# Run specific test file
pytest tests/test_data_processing.py -v

# Run specific test
pytest tests/test_model.py::TestModelTraining::test_pipeline_training -v

# Run with markers
pytest -m "not slow" tests/ -v

# Run tests in parallel (faster)
pytest tests/ -v -n auto
```

### Test Configuration

Configuration is defined in `pytest.ini`:
- Test discovery: `testpaths = tests`
- Test naming: `test_*.py` files, `Test*` classes, `test_*` methods
- Output: Verbose mode with short traceback
- Markers for slow/integration tests

### Shared Fixtures

Common fixtures are defined in `tests/conftest.py`:
- `sample_heart_disease_data` - Sample dataset with 100 records
- `numeric_features` - List of numeric columns
- `categorical_features` - List of categorical columns
- `test_data_dir` - Temporary directory for test files

---

## 🚀 CI/CD Pipeline

### GitHub Actions Workflows

#### 1. **Main CI/CD Pipeline** (`.github/workflows/mlops-ci-cd.yml`)

Triggered on: `push`, `pull_request`, `workflow_dispatch`

**Jobs:**

**Job 1: Linting** 🔍
- Tools: flake8, pylint, black, isort
- Checks:
  - Code style violations
  - Complexity analysis
  - Format checking
- Artifacts: Lint reports
- Status: Non-blocking (continue-on-error)

**Job 2: Unit Tests** 🧪
- Dependencies: Requires lint job
- Coverage:
  - Pytest runs all unit tests
  - Code coverage report generation
  - HTML coverage report
- Artifacts:
  - Test results
  - Coverage report
  - Coverage XML (for codecov)
- Tools: pytest, pytest-cov, codecov

**Job 3: Model Training** 🤖
- Dependencies: Requires test job to pass
- Tasks:
  - Executes `src/train_pipeline.py`
  - Generates training report
  - Validates model creation
- Artifacts:
  - Trained model
  - Training logs
  - Performance metrics
- Retention: 90 days

**Job 4: Integration Tests** 🔗
- Dependencies: Requires training job
- Tests:
  - Model loading from artifacts
  - End-to-end prediction pipeline
  - API compatibility
- Continues even if previous job fails

**Job 5: Pipeline Summary** 📋
- Aggregates all job results
- Generates execution summary
- Archives all artifacts

**Job 6: Notifications** 🔔
- Status reporting
- Optional Slack/email integration

### Example Workflow Output

```
✅ Linting: PASSED
  - flake8: No critical errors
  - pylint: Score 9.2/10
  - black: Code formatted

✅ Unit Tests: PASSED
  - 58 tests passed
  - Coverage: 85%
  - Execution time: 2m 15s

✅ Model Training: PASSED
  - Model trained with ROC-AUC: 0.92
  - Model size: 45.2 MB
  - Training time: 3m 42s

✅ Integration Tests: PASSED
  - Model loads correctly
  - Predictions working
  - Performance within SLA
```

#### 2. **Scheduled Retraining** (`.github/workflows/scheduled-retrain.yml`)

Triggered: Daily at 2 AM UTC (configurable via cron)

**Job:**
- Retrains model with latest data
- Validates model performance
- Uploads new model as artifact
- Logs execution details

**Configuration:**
```yaml
schedule:
  - cron: '0 2 * * *'  # Daily at 2 AM UTC
```

---

## 📊 Artifacts & Logging

### Generated Artifacts

#### From Linting Job
```
lint-reports/
├── flake8_report.txt
└── pylint_report.txt
```

#### From Test Job
```
test-results/
├── coverage_report/
│   ├── index.html
│   ├── status.json
│   └── ...
├── coverage_summary.txt
└── .coverage
```

#### From Training Job
```
model-artifacts/
├── models/
│   └── heart_disease_pipeline_prod.joblib
├── training_log.txt
└── training_report.json
```

#### From Integration Tests
```
integration-test/
└── integration_test.txt
```

#### Pipeline Summary
```
pipeline-summary/
├── pipeline_summary.md
└── all-artifacts/
    └── [all above artifacts]
```

### Artifact Retention

| Artifact | Retention | Purpose |
|----------|-----------|---------|
| Lint Reports | 30 days | Code quality tracking |
| Test Results | 30 days | Regression detection |
| Model Artifacts | 90 days | Rollback capability |
| Pipeline Summary | 90 days | Audit trail |

### Accessing Artifacts

1. **GitHub UI**: Actions → Workflow run → Artifacts
2. **Download**: Click artifact to download
3. **API**: Use GitHub API to retrieve programmatically

---

## 📝 Logging Details

### Training Log Format

```
[2024-01-05 10:15:30] Loading data...
[2024-01-05 10:15:35] Data loaded: 303 samples, 13 features
[2024-01-05 10:15:36] Splitting data: 242 train, 61 test
[2024-01-05 10:15:36] Training pipeline...
[2024-01-05 10:16:42] Model trained successfully
[2024-01-05 10:16:42] Test ROC-AUC: 0.9247
[2024-01-05 10:16:42] Saving model...
[2024-01-05 10:16:43] Model saved: models/heart_disease_pipeline_prod.joblib
```

### Test Output Format

```
tests/test_data_processing.py::TestDataLoading::test_load_csv PASSED
tests/test_data_processing.py::TestDataLoading::test_data_shape PASSED
tests/test_data_processing.py::TestDataValidation::test_age_range PASSED
...
====== 58 passed in 2.15s ======

Coverage Summary:
Name                                    Stmts   Miss  Cover
src/train_pipeline.py                      45      3    93%
deployment/app/main.py                     28      2    93%
TOTAL                                     120      8    93%
```

---

## 🔧 Local Development

### Setup

```bash
# Clone repository
git clone <repo-url>
cd mlops-assignment-final

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements-dev.txt
```

### Running Tests Locally

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=src --cov=deployment/app --cov-report=html

# Specific test class
pytest tests/test_model.py::TestModelTraining -v

# Tests with specific marker
pytest -m "not slow" tests/ -v
```

### Linting Locally

```bash
# Flake8
flake8 src/ deployment/app/ --statistics

# Pylint
pylint src/train_pipeline.py

# Black (check only)
black --check src/ deployment/app/

# Black (auto-format)
black src/ deployment/app/

# isort (check imports)
isort --check src/ deployment/app/
```

### Training Model Locally

```bash
# Ensure data exists
python src/train_pipeline.py

# Check MLflow UI
mlflow ui --host 0.0.0.0 --port 5000
```

---

## ✅ CI/CD Best Practices

### 1. **Test-Driven Development**
- Write tests before features
- Maintain >80% code coverage
- Test edge cases and error scenarios

### 2. **Code Quality**
- Use linters (flake8, pylint)
- Format code consistently (black, isort)
- Maximum line length: 127 characters

### 3. **Pipeline Efficiency**
- Run lint before tests
- Run tests before training
- Cache dependencies (pip)
- Use parallel test execution

### 4. **Artifact Management**
- Keep retention windows reasonable
- Archive critical artifacts
- Document artifact contents
- Version models properly

### 5. **Monitoring & Alerts**
- Check pipeline status regularly
- Monitor model performance
- Alert on failures
- Log all executions

---

## 🐛 Troubleshooting

### Issue: Tests Fail Locally But Pass in CI

**Solution:**
- Check Python version: `python --version`
- Reinstall dependencies: `pip install -r requirements-dev.txt --force-reinstall`
- Clear cache: `rm -rf .pytest_cache .coverage`

### Issue: Model Training Times Out

**Solution:**
- Increase timeout in workflow
- Reduce dataset size for testing
- Optimize preprocessing pipeline
- Check resource availability

### Issue: Coverage Not Reported

**Solution:**
- Ensure pytest-cov installed
- Check codecov token (if using)
- Review coverage configuration in pytest.ini

### Issue: Artifacts Not Uploading

**Solution:**
- Verify artifact paths exist
- Check disk space available
- Review GitHub Actions logs
- Ensure files aren't locked

---

## 📚 Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Flake8 Style Guide](https://flake8.pycqa.org/)
- [Coverage.py](https://coverage.readthedocs.io/)
- [MLflow Documentation](https://mlflow.org/docs/latest/)

---

## 🤝 Contributing

When contributing code:
1. Create feature branch
2. Write tests first
3. Ensure all tests pass locally
4. Ensure linting passes
5. Push to create pull request
6. Wait for CI/CD pipeline to pass
7. Request code review
8. Merge after approval

---

## 📞 Support

For questions or issues:
1. Check this documentation
2. Review workflow logs in GitHub Actions
3. Examine test output and coverage reports
4. Check artifact contents
5. Review git history for similar issues

---

**Last Updated**: January 5, 2024
