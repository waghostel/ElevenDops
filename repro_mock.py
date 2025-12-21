
from unittest.mock import MagicMock, AsyncMock

def test_mock_behavior():
    mock_doc_query = MagicMock()
    initial_count = 5
    
    # Setup side effect
    mock_doc_query.count.return_value.get.side_effect = [
        [[AsyncMock(value=initial_count)]], 
        [[AsyncMock(value=initial_count + 1)]]
    ]

    # Simulating Call 1
    query = mock_doc_query.count()
    snapshot = query.get()
    val = snapshot[0][0].value
    print(f"Call 1 value: {val}")
    if val != 5:
        print("FAIL 1")
    
    # Simulating Call 2
    query2 = mock_doc_query.count()
    snapshot2 = query2.get()
    val2 = snapshot2[0][0].value
    print(f"Call 2 value: {val2}")
    if val2 != 6:
        print("FAIL 2")

if __name__ == "__main__":
    try:
        test_mock_behavior()
        print("SUCCESS")
    except Exception as e:
        print(f"ERROR: {e}")
