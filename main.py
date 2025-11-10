import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from agents.coordinator import Coordinator

def main():
    # Load environment
    load_dotenv()
    
    # Connect to database
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        # Convert postgres:// to postgresql:// for newer SQLAlchemy versions
        database_url = database_url.replace('postgres://', 'postgresql://')
    engine = create_engine(database_url)
    
    # Read test code
    with open('data/bad_code.py', 'r') as f:
        code = f.read()
    
    # Run analysis
    coordinator = Coordinator(engine)
    results = coordinator.analyze_code(code, 'bad_code.py')
    
    # Print detailed results
    print("\n" + "="*60)
    print("ANALYSIS RESULTS")
    print("="*60)
    
    print(f"\nSECURITY ISSUES ({results['security']['count']}):")
    for issue in results['security']['issues']:
        print(f"   Line {issue['line']}: [{issue['severity']}] {issue['issue']}")
        print(f"      Fix: {issue['fix']}")
    
    print(f"\nQUALITY ISSUES ({results['quality']['count']}):")
    for issue in results['quality']['issues']:
        print(f"   Line {issue['line']}: [{issue['severity']}] {issue['issue']}")
        print(f"      Fix: {issue['fix']}")
    
    print(f"\nPERFORMANCE ISSUES ({results['performance']['count']}):")
    for issue in results['performance']['issues']:
        print(f"   Line {issue['line']}: [{issue['severity']}] {issue['issue']}")
        print(f"      Fix: {issue['fix']}")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()