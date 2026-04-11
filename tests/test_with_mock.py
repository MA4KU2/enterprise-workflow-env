#!/usr/bin/env python3
"""
Test script that mocks the LLM responses to validate the refactored system
without needing actual API keys.
"""
import os
import sys
from unittest.mock import patch, MagicMock
import json

# Set dummy credentials to avoid authentication errors
os.environ['HF_TOKEN'] = 'dummy-token'
os.environ['API_KEY'] = 'dummy-key'

def mock_llm_response(*args, **kwargs):
    """Mock LLM response that returns appropriate actions based on observation"""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = '{"action_type": "parse_requisition", "payload": {"req_id": "REQ-001"}, "rationale": "Starting workflow"}'
    return mock_response

def test_with_mock():
    """Test the system with mocked LLM"""
    sys.path.insert(0, '.')
    
    # Patch the OpenAI client
    with patch('inference.OpenAI') as mock_openai_class:
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.side_effect = mock_llm_response
        
        # Import after patching
        from inference import EnterpriseAgent
        
        print("=== Testing with Mocked LLM ===")
        
        # Test easy task
        print("\n--- Easy Task ---")
        agent = EnterpriseAgent(task_id='easy', max_steps=3)
        agent.run()
        
        # Test medium task  
        print("\n--- Medium Task ---")
        agent = EnterpriseAgent(task_id='medium', max_steps=5)
        agent.run()
        
        # Test hard task
        print("\n--- Hard Task ---")
        agent = EnterpriseAgent(task_id='hard', max_steps=7)
        agent.run()

if __name__ == '__main__':
    test_with_mock()
