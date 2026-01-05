"""
Shared pytest configuration and fixtures
"""
import pytest
import pandas as pd
import numpy as np
import tempfile
import os


@pytest.fixture(scope="session")
def test_data_dir():
    """Create a temporary directory for test data"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_heart_disease_data():
    """Create sample heart disease dataset"""
    np.random.seed(42)
    n_samples = 100
    
    return pd.DataFrame({
        'age': np.random.randint(30, 80, n_samples),
        'sex': np.random.randint(0, 2, n_samples),
        'cp': np.random.randint(0, 4, n_samples),
        'trestbps': np.random.randint(90, 200, n_samples),
        'chol': np.random.randint(150, 400, n_samples),
        'fbs': np.random.randint(0, 2, n_samples),
        'restecg': np.random.randint(0, 3, n_samples),
        'thalach': np.random.randint(60, 200, n_samples),
        'exang': np.random.randint(0, 2, n_samples),
        'oldpeak': np.random.uniform(0, 5, n_samples),
        'slope': np.random.randint(0, 3, n_samples),
        'ca': np.random.randint(0, 5, n_samples),
        'thal': np.random.randint(1, 4, n_samples),
        'target': np.random.randint(0, 2, n_samples)
    })


@pytest.fixture
def numeric_features():
    """List of numeric features"""
    return ['age', 'trestbps', 'chol', 'thalach', 'oldpeak', 'ca']


@pytest.fixture
def categorical_features():
    """List of categorical features"""
    return ['sex', 'cp', 'fbs', 'restecg', 'exang', 'slope', 'thal']
