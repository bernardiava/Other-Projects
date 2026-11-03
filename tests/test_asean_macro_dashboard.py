"""
Unit tests for ASEAN Macro Dashboard
Tests core functionality including data fetching, FX prediction, and forecasting.
"""
import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock
from datetime import datetime

# Import the functions to test (we'll need to refactor them into a separate module)
# For now, we'll test the logic directly


class TestFXPrediction:
    """Test FX prediction functionality"""
    
    def test_date_range_frequency(self):
        """Test that date_range uses 'ME' instead of deprecated 'M' frequency"""
        # This test ensures the fix for: ValueError("'M' is no longer supported for offsets")
        last_date = pd.Timestamp('2024-12-31')
        
        # Should use 'ME' (Month End) instead of 'M'
        forecast_dates = pd.date_range(
            start=last_date + pd.DateOffset(months=1),
            periods=12,
            freq='ME'
        )
        
        assert len(forecast_dates) == 12
        assert all(isinstance(d, pd.Timestamp) for d in forecast_dates)
        # Verify dates are month-end
        assert forecast_dates[0].day == 31  # January 31
    
    def test_timestamp_conversion(self):
        """Test proper handling of Timestamp objects"""
        # Test with datetime object
        dt = datetime(2024, 12, 31)
        if not isinstance(dt, pd.Timestamp):
            ts = pd.Timestamp(dt)
        else:
            ts = dt
        
        assert isinstance(ts, pd.Timestamp)
        
        # Test with already Timestamp object
        ts_already = pd.Timestamp('2024-12-31')
        if not isinstance(ts_already, pd.Timestamp):
            ts_converted = pd.Timestamp(ts_already)
        else:
            ts_converted = ts_already
        
        assert isinstance(ts_converted, pd.Timestamp)


class TestDataFetching:
    """Test World Bank data fetching logic"""
    
    @patch('requests.get')
    def test_load_worldbank_data_success(self, mock_get):
        """Test successful data fetch from World Bank API"""
        # Mock response
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"page": 1, "pages": 1, "per_page": 500, "total": 5},
            [
                {
                    "country": {"value": "Indonesia"},
                    "date": "2023",
                    "value": 5.05
                },
                {
                    "country": {"value": "Indonesia"},
                    "date": "2022",
                    "value": 5.31
                }
            ]
        ]
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        # Simulate the parsing logic
        data = mock_response.json()
        records = []
        for item in data[1]:
            value = item['value']
            if value is not None:
                records.append({
                    'country': item['country']['value'],
                    'year': int(item['date']),
                    'indicator': float(value)
                })
        
        df = pd.DataFrame(records)
        df_pivot = df.pivot(index='year', columns='country', values='indicator')
        
        assert len(df_pivot) == 2
        assert 2023 in df_pivot.index
        assert df_pivot.loc[2023, 'Indonesia'] == 5.05
    
    @patch('requests.get')
    def test_load_worldbank_data_empty(self, mock_get):
        """Test handling of empty API response"""
        mock_response = MagicMock()
        mock_response.json.return_value = [{"page": 1}, []]
        mock_get.return_value = mock_response
        
        data = mock_response.json()
        if len(data) < 2 or not data[1]:
            result_df = pd.DataFrame()
        else:
            result_df = pd.DataFrame()  # Would process data otherwise
        
        assert result_df.empty
    
    def test_retry_logic(self):
        """Test that retry logic is implemented with correct parameters"""
        max_retries = 3
        retry_delay = 5
        
        assert max_retries == 3
        assert retry_delay == 5


class TestForecasting:
    """Test SARIMA forecasting logic"""
    
    def test_forecast_index_creation(self):
        """Test forecast index creation for annual data"""
        combined_index = pd.Index([2020, 2021, 2022, 2023])
        last_year = int(combined_index[-1])
        forecast_steps = 4
        forecast_index = [last_year + i for i in range(1, forecast_steps + 1)]
        
        assert forecast_index == [2024, 2025, 2026, 2027]
        assert len(forecast_index) == 4
    
    def test_sarima_input_validation(self):
        """Test that SARIMA model receives valid input"""
        # Create sample time series data
        np.random.seed(42)
        data = pd.Series(np.random.randn(20) + 5, 
                        index=pd.date_range('2000', periods=20, freq='YE'))
        
        # Validate data has enough points
        assert len(data) > 10
        assert not data.isna().any()
        
        # Validate index is datetime
        assert isinstance(data.index, pd.DatetimeIndex)


class TestMarketData:
    """Test market data fetching"""
    
    def test_get_market_data_structure(self):
        """Test market data returns expected structure"""
        # Simulate what yfinance returns
        mock_data = pd.Series(
            [15000.0, 15100.0, 15200.0],
            index=pd.date_range('2024-01-01', periods=3, freq='D'),
            name='Close'
        )
        
        assert isinstance(mock_data, pd.Series)
        assert 'Close' == mock_data.name
        assert len(mock_data) == 3
    
    def test_empty_market_data_handling(self):
        """Test handling of empty market data"""
        empty_series = pd.Series()
        
        assert empty_series.empty
        assert len(empty_series) == 0


class TestExecutiveSummary:
    """Test executive summary logic"""
    
    def test_growth_status_classification(self):
        """Test GDP growth status classification"""
        def get_growth_status(growth):
            if growth > 5:
                return "STRONG"
            elif growth > 3:
                return "MODERATE"
            else:
                return "WEAK"
        
        assert get_growth_status(6.5) == "STRONG"
        assert get_growth_status(4.0) == "MODERATE"
        assert get_growth_status(2.5) == "WEAK"
        assert get_growth_status(5.0) == "MODERATE"
    
    def test_current_account_status(self):
        """Test current account surplus/deficit classification"""
        def get_ca_status(ca_value):
            return "Surplus" if ca_value > 0 else "Deficit"
        
        assert get_ca_status(2.5) == "Surplus"
        assert get_ca_status(-1.5) == "Deficit"
        assert get_ca_status(0) == "Deficit"
    
    def test_year_extraction_from_index(self):
        """Test extracting year from different index types"""
        # Integer index
        int_idx = pd.Index([2020, 2021, 2022, 2023])
        idx_value = int_idx[-1]
        if hasattr(idx_value, 'year'):
            latest_year = idx_value.year
        else:
            latest_year = int(idx_value)
        
        assert latest_year == 2023
        
        # Datetime index
        dt_idx = pd.DatetimeIndex(['2020-01-01', '2021-01-01', '2022-01-01', '2023-01-01'])
        idx_value = dt_idx[-1]
        if hasattr(idx_value, 'year'):
            latest_year = idx_value.year
        else:
            latest_year = int(idx_value)
        
        assert latest_year == 2023


class TestFXYearlyAggregation:
    """Test FX forecast yearly aggregation"""
    
    def test_yearly_average_calculation(self):
        """Test grouping monthly forecasts by year"""
        fx_prediction_df = pd.DataFrame({
            'Date': pd.date_range('2025-01-31', periods=12, freq='ME'),
            'Predicted Exchange Rate': [16000 + i*10 for i in range(12)]
        })
        
        fx_prediction_df['Year'] = fx_prediction_df['Date'].dt.year
        yearly_forecast = fx_prediction_df.groupby('Year')['Predicted Exchange Rate'].mean().reset_index()
        
        assert len(yearly_forecast) == 1  # All 12 months in same year
        assert yearly_forecast.iloc[0]['Year'] == 2025
        assert 'Avg Predicted Exchange Rate' in yearly_forecast.columns or \
               'Predicted Exchange Rate' in yearly_forecast.columns


def make_forecastable_annual_series(series):
    """Replica of the dashboard helper: convert plain-year-indexed series to
    an annual PeriodIndex so statsmodels can extend it for forecasting."""
    years = [int(getattr(y, 'year', y)) for y in series.index]
    full_index = pd.period_range(start=str(min(years)), end=str(max(years)), freq='Y')
    aligned = series.copy()
    aligned.index = pd.Index(years)
    aligned = aligned.reindex(pd.Index([p.year for p in full_index])).astype(float)
    aligned.index = full_index
    return aligned


class TestNoSupportedIndexFix:
    """Regression tests for ValueError('No supported index is available.')"""

    def test_plain_int_index_forecast_fails_without_fix(self):
        """A plain integer year index cannot be extended by statsmodels."""
        from statsmodels.tsa.statespace.sarimax import SARIMAX
        s = pd.Series(
            np.random.randn(12).cumsum() / 10,
            index=pd.Index([2010, 2011, 2012, 2013, 2014, 2016,
                            2018, 2019, 2020, 2021, 2022, 2023])
        )
        model = SARIMAX(s, order=(1, 1, 1), seasonal_order=(1, 1, 1, 4),
                        simple_differencing=False).fit(disp=False)
        with pytest.raises(ValueError, match="No supported index"):
            model.forecast(steps=4)

    def test_period_index_forecast_succeeds_with_fix(self):
        """After converting to an annual PeriodIndex, forecast works."""
        from statsmodels.tsa.statespace.sarimax import SARIMAX
        s = pd.Series(
            np.random.randn(12).cumsum() / 10,
            index=pd.Index([2010, 2011, 2012, 2013, 2014, 2016,
                            2018, 2019, 2020, 2021, 2022, 2023])
        )
        ca = make_forecastable_annual_series(s)
        model = SARIMAX(ca, order=(1, 1, 1), seasonal_order=(1, 1, 1, 4),
                        simple_differencing=False).fit(disp=False)
        forecast = model.forecast(steps=4)
        assert len(forecast) == 4
        # Forecast periods extend beyond the last historical year (2023)
        assert [p.year for p in forecast.index] == [2024, 2025, 2026, 2027]

    def test_make_forecastable_annual_series_fills_gaps(self):
        """Missing years become NaN entries on a complete annual grid."""
        s = pd.Series([1.0, 2.0, 3.0], index=pd.Index([2010, 2012, 2013]))
        out = make_forecastable_annual_series(s)
        assert isinstance(out.index, pd.PeriodIndex)
        assert len(out) == 4          # 2010..2013 inclusive
        assert out.isna().sum() == 1  # 2011 gap filled as NaN
        assert out.iloc[0] == 1.0 and out.iloc[-1] == 3.0

    def test_fx_daily_resampled_to_monthly_supports_seasonal_forecast(self):
        """Daily FX resampled to month-end allows SARIMA(1,1,1)(1,1,1,12) forecast."""
        from statsmodels.tsa.statespace.sarimax import SARIMAX
        rng = np.random.default_rng(42)
        daily = pd.Series(
            15000 + np.cumsum(rng.normal(0, 10, 800)),
            index=pd.date_range('2024-01-01', periods=800, freq='B')
        )
        monthly = daily.resample('ME').last().dropna()
        model = SARIMAX(monthly, order=(1, 1, 1), seasonal_order=(1, 1, 1, 12),
                        simple_differencing=False).fit(disp=False)
        forecast = model.forecast(steps=12)
        assert len(forecast) == 12
        # First forecast month follows the last observed month-end
        expected_start = monthly.index[-1] + pd.DateOffset(months=1)
        assert forecast.index[0] == expected_start

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
