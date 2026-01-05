"""
Unit tests for model training and inference
Tests model creation, training, and prediction
"""
import pytest
import pandas as pd
import numpy as np
import joblib
import tempfile
import os
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score


class TestModelCreation:
    """Test model creation and structure"""
    
    def test_random_forest_creation(self):
        """Test RandomForest model can be created"""
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=2,
            random_state=42
        )
        assert model is not None
        assert model.n_estimators == 100
        assert model.max_depth == 10
    
    def test_preprocessing_pipeline(self):
        """Test preprocessing pipeline creation"""
        numeric_features = ['age', 'trestbps', 'chol', 'thalach', 'oldpeak', 'ca']
        categorical_features = ['sex', 'cp', 'fbs', 'restecg', 'exang', 'slope', 'thal']
        
        preprocessor = ColumnTransformer([
            ('num', Pipeline([
                ('imputer', SimpleImputer(strategy='median')),
                ('scaler', StandardScaler())
            ]), numeric_features),
            ('cat', Pipeline([
                ('imputer', SimpleImputer(strategy='most_frequent')),
                ('onehot', OneHotEncoder(drop='first', sparse_output=False, handle_unknown='ignore'))
            ]), categorical_features)
        ])
        
        assert preprocessor is not None
        assert len(preprocessor.transformers) == 2
    
    def test_full_pipeline_creation(self):
        """Test full ML pipeline creation"""
        numeric_features = ['age', 'trestbps', 'chol', 'thalach', 'oldpeak', 'ca']
        categorical_features = ['sex', 'cp', 'fbs', 'restecg', 'exang', 'slope', 'thal']
        
        preprocessor = ColumnTransformer([
            ('num', Pipeline([
                ('imputer', SimpleImputer(strategy='median')),
                ('scaler', StandardScaler())
            ]), numeric_features),
            ('cat', Pipeline([
                ('imputer', SimpleImputer(strategy='most_frequent')),
                ('onehot', OneHotEncoder(drop='first', sparse_output=False, handle_unknown='ignore'))
            ]), categorical_features)
        ])
        
        pipeline = Pipeline([
            ('preprocessor', preprocessor),
            ('classifier', RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42))
        ])
        
        assert pipeline is not None
        assert 'preprocessor' in pipeline.named_steps
        assert 'classifier' in pipeline.named_steps


class TestModelTraining:
    """Test model training"""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample data"""
        np.random.seed(42)
        n_samples = 100
        data = {
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
        }
        return pd.DataFrame(data)
    
    def test_model_training(self, sample_data):
        """Test model training"""
        X = sample_data.drop('target', axis=1)
        y = sample_data['target']
        
        model = RandomForestClassifier(n_estimators=50, max_depth=5, random_state=42)
        model.fit(X, y)
        
        assert model is not None
        assert hasattr(model, 'predict')
        assert hasattr(model, 'predict_proba')
    
    def test_pipeline_training(self, sample_data):
        """Test full pipeline training"""
        X = sample_data.drop('target', axis=1)
        y = sample_data['target']
        
        numeric_features = ['age', 'trestbps', 'chol', 'thalach', 'oldpeak', 'ca']
        categorical_features = ['sex', 'cp', 'fbs', 'restecg', 'exang', 'slope', 'thal']
        
        preprocessor = ColumnTransformer([
            ('num', Pipeline([
                ('imputer', SimpleImputer(strategy='median')),
                ('scaler', StandardScaler())
            ]), numeric_features),
            ('cat', Pipeline([
                ('imputer', SimpleImputer(strategy='most_frequent')),
                ('onehot', OneHotEncoder(drop='first', sparse_output=False, handle_unknown='ignore'))
            ]), categorical_features)
        ])
        
        pipeline = Pipeline([
            ('preprocessor', preprocessor),
            ('classifier', RandomForestClassifier(n_estimators=50, max_depth=5, random_state=42))
        ])
        
        pipeline.fit(X, y)
        assert pipeline is not None
    
    def test_model_convergence(self, sample_data):
        """Test model converges on training data"""
        X = sample_data.drop('target', axis=1)
        y = sample_data['target']
        
        model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
        model.fit(X, y)
        
        train_pred = model.predict(X)
        train_accuracy = accuracy_score(y, train_pred)
        
        # Model should perform reasonably well on training data
        assert train_accuracy > 0.5


class TestModelPrediction:
    """Test model prediction"""
    
    @pytest.fixture
    def trained_model(self):
        """Create and train a model"""
        np.random.seed(42)
        n_samples = 100
        data = {
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
            'target': np.random.randint(0, 2, n_samples)
        }
        df = pd.DataFrame(data)
        X = df.drop('target', axis=1)
        y = df['target']
        
        model = RandomForestClassifier(n_estimators=50, random_state=42)
        model.fit(X, y)
        return model
    
    def test_predict_shape(self, trained_model):
        """Test prediction output shape"""
        np.random.seed(42)
        test_data = pd.DataFrame({
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
            'ca': [0, 1, 0]
        })
        
        predictions = trained_model.predict(test_data)
        assert len(predictions) == 3
        assert set(predictions).issubset({0, 1})
    
    def test_predict_proba_shape(self, trained_model):
        """Test probability prediction output shape"""
        test_data = pd.DataFrame({
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
            'ca': [0, 1, 0]
        })
        
        probabilities = trained_model.predict_proba(test_data)
        assert probabilities.shape == (3, 2)
        assert np.allclose(probabilities.sum(axis=1), 1)
    
    def test_predict_proba_valid(self, trained_model):
        """Test probability predictions are valid"""
        test_data = pd.DataFrame({
            'age': [45],
            'sex': [1],
            'cp': [0],
            'trestbps': [120],
            'chol': [200],
            'fbs': [0],
            'restecg': [0],
            'thalach': [150],
            'exang': [0],
            'oldpeak': [0.0],
            'slope': [1],
            'ca': [0]
        })
        
        probabilities = trained_model.predict_proba(test_data)
        assert (probabilities >= 0).all()
        assert (probabilities <= 1).all()


class TestModelEvaluation:
    """Test model evaluation metrics"""
    
    @pytest.fixture
    def eval_data(self):
        """Create evaluation data"""
        np.random.seed(42)
        n_samples = 100
        data = {
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
        }
        return pd.DataFrame(data)
    
    def test_accuracy_metric(self, eval_data):
        """Test accuracy metric calculation"""
        X = eval_data.drop('target', axis=1)
        y = eval_data['target']
        
        model = RandomForestClassifier(n_estimators=50, random_state=42)
        model.fit(X, y)
        
        predictions = model.predict(X)
        accuracy = accuracy_score(y, predictions)
        
        assert 0 <= accuracy <= 1
        assert accuracy > 0.5
    
    def test_precision_recall_f1(self, eval_data):
        """Test precision, recall, F1 metrics"""
        X = eval_data.drop('target', axis=1)
        y = eval_data['target']
        
        model = RandomForestClassifier(n_estimators=50, random_state=42)
        model.fit(X, y)
        
        predictions = model.predict(X)
        precision = precision_score(y, predictions, zero_division=0)
        recall = recall_score(y, predictions, zero_division=0)
        f1 = f1_score(y, predictions, zero_division=0)
        
        assert 0 <= precision <= 1
        assert 0 <= recall <= 1
        assert 0 <= f1 <= 1
    
    def test_roc_auc(self, eval_data):
        """Test ROC-AUC metric"""
        X = eval_data.drop('target', axis=1)
        y = eval_data['target']
        
        model = RandomForestClassifier(n_estimators=50, random_state=42)
        model.fit(X, y)
        
        probabilities = model.predict_proba(X)[:, 1]
        auc = roc_auc_score(y, probabilities)
        
        assert 0 <= auc <= 1
        assert auc > 0.5


class TestModelPersistence:
    """Test model saving and loading"""
    
    @pytest.fixture
    def trained_model(self):
        """Create and train a model"""
        np.random.seed(42)
        n_samples = 100
        data = {
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
            'target': np.random.randint(0, 2, n_samples)
        }
        df = pd.DataFrame(data)
        X = df.drop('target', axis=1)
        y = df['target']
        
        model = RandomForestClassifier(n_estimators=50, random_state=42)
        model.fit(X, y)
        return model
    
    def test_model_save_and_load(self, trained_model):
        """Test saving and loading model"""
        with tempfile.TemporaryDirectory() as tmpdir:
            model_path = os.path.join(tmpdir, 'test_model.joblib')
            
            # Save model
            joblib.dump(trained_model, model_path)
            assert os.path.exists(model_path)
            
            # Load model
            loaded_model = joblib.load(model_path)
            assert loaded_model is not None
    
    def test_loaded_model_prediction(self, trained_model):
        """Test prediction with loaded model"""
        with tempfile.TemporaryDirectory() as tmpdir:
            model_path = os.path.join(tmpdir, 'test_model.joblib')
            
            # Save and load
            joblib.dump(trained_model, model_path)
            loaded_model = joblib.load(model_path)
            
            # Test prediction
            test_data = pd.DataFrame({
                'age': [45, 50],
                'sex': [1, 0],
                'cp': [0, 1],
                'trestbps': [120, 130],
                'chol': [200, 220],
                'fbs': [0, 1],
                'restecg': [0, 1],
                'thalach': [150, 160],
                'exang': [0, 0],
                'oldpeak': [0.0, 0.5],
                'slope': [1, 2],
                'ca': [0, 1]
            })
            
            original_pred = trained_model.predict(test_data)
            loaded_pred = loaded_model.predict(test_data)
            
            assert np.array_equal(original_pred, loaded_pred)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
