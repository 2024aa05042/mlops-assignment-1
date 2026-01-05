"""
Unit tests for data processing pipeline
Tests data loading, validation, and preprocessing
"""
import pytest
import pandas as pd
import numpy as np
import os
import tempfile
from pathlib import Path
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline


class TestDataLoading:
    """Test data loading and validation"""
    
    @pytest.fixture
    def sample_csv(self):
        """Create a temporary CSV file for testing"""
        data = {
            'age': [45, 50, 60, 35, 55],
            'sex': [1, 0, 1, 1, 0],
            'cp': [0, 1, 3, 2, 1],
            'trestbps': [120, 130, 145, 110, 125],
            'chol': [200, 220, 233, 190, 240],
            'fbs': [0, 1, 1, 0, 0],
            'restecg': [0, 1, 0, 0, 1],
            'thalach': [150, 160, 150, 170, 140],
            'exang': [0, 0, 0, 1, 0],
            'oldpeak': [0.0, 0.5, 2.3, 0.0, 1.0],
            'slope': [1, 2, 0, 1, 2],
            'ca': [0, 1, 0, 0, 2],
            'thal': [3, 3, 1, 3, 2],
            'target': [0, 1, 1, 0, 1]
        }
        df = pd.DataFrame(data)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            df.to_csv(f.name, index=False)
            temp_path = f.name
        
        yield temp_path
        os.unlink(temp_path)
    
    def test_load_csv(self, sample_csv):
        """Test CSV loading"""
        df = pd.read_csv(sample_csv)
        assert len(df) == 5
        assert 'target' in df.columns
        assert len(df.columns) == 14
    
    def test_data_shape(self, sample_csv):
        """Test data shape validation"""
        df = pd.read_csv(sample_csv)
        assert df.shape == (5, 14)
        assert not df.isnull().any().any()
    
    def test_target_column_exists(self, sample_csv):
        """Test that target column exists"""
        df = pd.read_csv(sample_csv)
        assert 'target' in df.columns
        assert df['target'].dtype in ['int64', 'int32']


class TestDataPreprocessing:
    """Test data preprocessing pipeline"""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample data with missing values"""
        data = {
            'age': [45, 50, np.nan, 35, 55],
            'sex': [1, 0, 1, 1, 0],
            'cp': [0, 1, 3, 2, np.nan],
            'trestbps': [120, 130, 145, 110, 125],
            'chol': [200, 220, 233, 190, 240],
            'fbs': [0, 1, 1, 0, 0],
            'restecg': [0, 1, 0, 0, 1],
            'thalach': [150, 160, 150, 170, 140],
            'exang': [0, 0, 0, 1, 0],
            'oldpeak': [0.0, 0.5, 2.3, 0.0, 1.0],
            'slope': [1, 2, 0, 1, 2],
            'ca': [0, 1, 0, 0, 2],
            'thal': [3, 3, 1, 3, 2],
            'target': [0, 1, 1, 0, 1]
        }
        return pd.DataFrame(data)
    
    def test_missing_value_handling(self, sample_data):
        """Test handling of missing values"""
        # Check that there are missing values
        assert sample_data.isnull().any().any()
        
        # Test numeric imputation
        numeric_imputer = SimpleImputer(strategy='median')
        numeric_cols = ['age', 'trestbps', 'chol', 'thalach', 'oldpeak', 'ca']
        numeric_data = sample_data[numeric_cols]
        imputed = numeric_imputer.fit_transform(numeric_data)
        
        assert not np.isnan(imputed).any()
    
    def test_feature_scaling(self, sample_data):
        """Test feature scaling"""
        X = sample_data.drop('target', axis=1)
        y = sample_data['target']
        
        # Fill missing values first
        X_filled = X.fillna(X.median(numeric_only=True))
        
        numeric_cols = ['age', 'trestbps', 'chol', 'thalach', 'oldpeak', 'ca']
        scaler = StandardScaler()
        
        scaled = scaler.fit_transform(X_filled[numeric_cols])
        
        # Check that features are scaled (mean ~0, std ~1)
        assert np.allclose(scaled.mean(axis=0), 0, atol=1e-10)
        assert np.allclose(scaled.std(axis=0), 1, atol=1e-1)
    
    def test_categorical_encoding(self, sample_data):
        """Test categorical encoding"""
        X = sample_data.drop('target', axis=1)
        categorical_cols = ['sex', 'cp', 'fbs', 'restecg', 'exang', 'slope', 'thal']
        
        encoder = OneHotEncoder(drop='first', sparse_output=False, handle_unknown='ignore')
        encoded = encoder.fit_transform(X[categorical_cols])
        
        assert encoded.shape[0] == X.shape[0]
        assert encoded.dtype == float
        assert not np.isnan(encoded).any()


class TestDataValidation:
    """Test data validation rules"""
    
    @pytest.fixture
    def valid_data(self):
        """Create valid data"""
        return pd.DataFrame({
            'age': [45, 50, 60],
            'sex': [1, 0, 1],
            'cp': [0, 1, 3],
            'trestbps': [120, 130, 145],
            'chol': [200, 220, 233],
            'fbs': [0, 1, 1],
            'restecg': [0, 1, 0],
            'thalach': [150, 160, 150],
            'exang': [0, 0, 0],
            'oldpeak': [0.0, 0.5, 2.3],
            'slope': [1, 2, 0],
            'ca': [0, 1, 0],
            'thal': [3, 3, 1],
            'target': [0, 1, 1]
        })
    
    def test_age_range(self, valid_data):
        """Test age is within valid range"""
        assert (valid_data['age'] > 0).all()
        assert (valid_data['age'] < 150).all()
    
    def test_binary_features(self, valid_data):
        """Test binary features have correct values"""
        binary_cols = ['sex', 'fbs', 'exang']
        for col in binary_cols:
            assert set(valid_data[col].unique()).issubset({0, 1})
    
    def test_categorical_ranges(self, valid_data):
        """Test categorical features are in valid ranges"""
        assert (valid_data['cp'] >= 0).all() and (valid_data['cp'] <= 3).all()
        assert (valid_data['restecg'] >= 0).all() and (valid_data['restecg'] <= 2).all()
        assert (valid_data['slope'] >= 0).all() and (valid_data['slope'] <= 2).all()
        assert (valid_data['thal'] >= 0).all() and (valid_data['thal'] <= 3).all()
    
    def test_target_binary(self, valid_data):
        """Test target is binary"""
        assert set(valid_data['target'].unique()).issubset({0, 1})


class TestDataSplitting:
    """Test train-test split"""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample data"""
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
    
    def test_train_test_split(self, sample_data):
        """Test train-test split functionality"""
        from sklearn.model_selection import train_test_split
        
        X = sample_data.drop('target', axis=1)
        y = sample_data['target']
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        assert len(X_train) + len(X_test) == len(X)
        assert len(X_test) == int(0.2 * len(X))
        assert len(y_train) == len(X_train)
        assert len(y_test) == len(X_test)
    
    def test_stratified_split(self, sample_data):
        """Test stratified split preserves class distribution"""
        from sklearn.model_selection import train_test_split
        
        X = sample_data.drop('target', axis=1)
        y = sample_data['target']
        
        original_ratio = y.value_counts(normalize=True)
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        train_ratio = y_train.value_counts(normalize=True)
        test_ratio = y_test.value_counts(normalize=True)
        
        # Check that distributions are similar (within tolerance)
        for idx in original_ratio.index:
            assert abs(original_ratio[idx] - train_ratio[idx]) < 0.1
            assert abs(original_ratio[idx] - test_ratio[idx]) < 0.1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
