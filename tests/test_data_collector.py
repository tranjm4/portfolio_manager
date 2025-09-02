import pytest
from unittest.mock import Mock, MagicMock, patch, mock_open

from src.data.collector import DataCollector

class TestDataCollector:
    @pytest.fixture
    def mock_yf_dependency(self):
        with patch("src.data.collector.yf") as mock_yf:
            yield mock_yf
    
    @pytest.fixture
    def mock_tickers_file(self):
        with patch("builtins.open", mock_open(read_data="A\nB\nC")) as mock_file:
            yield mock_file
    
    def test_data_collector_init(self, mock_yf_dependency):
        """Tests for expected attributes and methods"""
        mock_yf = mock_yf_dependency
        mock_yf.Tickers = Mock()
        with patch.object(DataCollector, "read_tickers") as mock_read_tickers:
            mock_read_tickers.return_value = ["A", "B", "C"]
            dc = DataCollector()
        
            mock_yf.Tickers.assert_called_once()
            mock_read_tickers.assert_called_once()
    
    def test_data_collector_read_tickers(self, mock_yf_dependency, mock_tickers_file):
        """Tests for the reading of the tickers file"""
        mock_yf = mock_yf_dependency
        mock_yf.Tickers = Mock()
        
        dc = DataCollector()
        mock_yf.Tickers.assert_called_once_with(["A","B","C"])
        
    def test_data_collector_run(self, mock_yf_dependency, mock_tickers_file):
        """Tests the main run loop"""
        mock_yf = mock_yf_dependency
        mock_yf.Tickers.return_value.live = Mock()
        
        dc = DataCollector()
        
        # Test normal execution
        dc.run()
        
        dc.yf.live.assert_called_once_with(message_handler=dc.handle_message)
        
    def test_data_collector_run_keyboard_interrupt(self, mock_yf_dependency, mock_tickers_file):
        """Tests the main run loop handles KeyboardInterrupt"""
        mock_yf = mock_yf_dependency
        mock_yf.Tickers.return_value.live = Mock(side_effect=KeyboardInterrupt())
        
        dc = DataCollector()
        
        # Should handle KeyboardInterrupt gracefully
        dc.run()  # Should not raise exception
        
        dc.yf.live.assert_called_once_with(message_handler=dc.handle_message)
    
    def test_data_collector_run_keyboard_interrupt_partway(self, mock_yf_dependency, mock_tickers_file):
        """Tests the main loop handles KeyboardInterrupt after a few iterations"""
        mock_yf = mock_yf_dependency
        mock_yf.Tickers.return_value.live = Mock(side_effect=["hello", "world", KeyboardInterrupt()])
        
        dc = DataCollector()
        dc.handle_message = Mock()
        
        dc.run()
        
        dc.handle_message.call_count == 2
        
    def test_convert_string_to_datetime(self, mock_yf_dependency, mock_tickers_file):
        """Tests the helper function that converts a string integer to a datetime"""
        dc = DataCollector()
        time = 1756386138000
        assert dc._convert_str_to_datetime(str(time)) == "2025-08-28 06:02:18"
        assert dc._convert_str_to_datetime(str(time + 1000)) == "2025-08-28 06:02:19"
        assert dc._convert_str_to_datetime(str(time + 60000)) == "2025-08-28 06:03:18"