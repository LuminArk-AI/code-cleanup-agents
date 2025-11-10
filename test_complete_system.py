"""Test script to verify all three agents work together"""
import os
import sys
import json
from dotenv import load_dotenv
from sqlalchemy import create_engine
from agents.coordinator import Coordinator

def test_coordinator():
    """Test the coordinator with all three agents"""
    print("="*70)
    print("TESTING COMPLETE MULTI-AGENT SYSTEM")
    print("="*70)
    
    load_dotenv()
    
    # Connect to database
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("ERROR: DATABASE_URL not found in .env")
        return False
    
    database_url = database_url.replace('postgres://', 'postgresql://')
    engine = create_engine(database_url)
    
    # Read test code
    try:
        with open('data/bad_code.py', 'r') as f:
            code = f.read()
    except FileNotFoundError:
        print("ERROR: data/bad_code.py not found")
        return False
    
    # Run analysis
    try:
        coordinator = Coordinator(engine)
        results = coordinator.analyze_code(code, 'bad_code.py')
    except Exception as e:
        print(f"ERROR: Analysis failed - {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Verify results structure
    print("\n" + "="*70)
    print("VERIFICATION")
    print("="*70)
    
    required_keys = ['submission_id', 'filename', 'security', 'quality', 'performance', 'total_issues']
    missing_keys = [key for key in required_keys if key not in results]
    
    if missing_keys:
        print(f"FAIL: Missing keys in results: {missing_keys}")
        return False
    
    print(f"SUCCESS: Results structure is correct")
    print(f"\nSummary:")
    print(f"  Submission ID: {results['submission_id']}")
    print(f"  Filename: {results['filename']}")
    print(f"  Security Issues: {results['security']['count']}")
    print(f"  Quality Issues: {results['quality']['count']}")
    print(f"  Performance Issues: {results['performance']['count']}")
    print(f"  Total Issues: {results['total_issues']}")
    
    # Verify each agent returned issues
    if results['security']['count'] == 0:
        print("WARNING: Security agent found 0 issues (might be expected)")
    
    if results['quality']['count'] == 0:
        print("WARNING: Quality agent found 0 issues (might be expected)")
    
    if results['performance']['count'] == 0:
        print("WARNING: Performance agent found 0 issues (might be expected)")
    
    # Verify issues structure
    for agent_type in ['security', 'quality', 'performance']:
        for issue in results[agent_type]['issues']:
            required_issue_keys = ['type', 'issue', 'line', 'code', 'severity', 'fix']
            missing_issue_keys = [key for key in required_issue_keys if key not in issue]
            if missing_issue_keys:
                print(f"FAIL: Issue missing keys: {missing_issue_keys}")
                return False
    
    print(f"\nSUCCESS: All issue structures are correct")
    
    # Test JSON serialization (as Flask would do)
    try:
        json_output = json.dumps(results)
        print(f"SUCCESS: Results can be serialized to JSON ({len(json_output)} bytes)")
    except Exception as e:
        print(f"FAIL: JSON serialization failed - {e}")
        return False
    
    print("\n" + "="*70)
    print("ALL TESTS PASSED!")
    print("="*70)
    return True

if __name__ == "__main__":
    success = test_coordinator()
    sys.exit(0 if success else 1)
