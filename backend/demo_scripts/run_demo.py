#!/usr/bin/env python3
"""
Quick Demo Launcher
Convenient script to run common demo scenarios
"""
import sys
import subprocess


def print_menu():
    """Display the demo menu"""
    print("\n" + "=" * 60)
    print("🏥 PET HEALTH API - DEMO LAUNCHER")
    print("=" * 60)
    print("\nAvailable Demos:")
    print("\n1. 🔌 Ollama Connectivity Test")
    print("   Quick test to verify Ollama is running and responding")
    print("   Runtime: ~5 seconds")
    
    print("\n2. 🏥 AI Veterinary Analysis Demo")
    print("   Comprehensive demo with 3 realistic cases")
    print("   Shows emergency, high, and medium urgency scenarios")
    print("   Runtime: ~30-60 seconds")
    
    print("\n3. 🔧 Service Integration Test")
    print("   Tests SymptomService layer with AI integration")
    print("   Validates service-level functionality")
    print("   Runtime: ~20-40 seconds")
    
    print("\n4. 🔄 End-to-End Workflow Test")
    print("   Complete API test: registration → auth → pet management")
    print("   Tests full backend workflow with HTTP requests")
    print("   Runtime: ~10-20 seconds")
    
    print("\n5. ℹ️  Show README")
    print("   Display detailed information about demo scripts")
    
    print("\n0. 🚪 Exit")
    print("\n" + "=" * 60)


def run_script(script_name):
    """Run a demo script"""
    try:
        print(f"\n▶️  Running {script_name}...\n")
        result = subprocess.run(
            ["python", f"demo_scripts/{script_name}"],
            check=False
        )
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running script: {e}")
        return False


def show_readme():
    """Display the README file"""
    try:
        with open("demo_scripts/README.md", "r") as f:
            print("\n" + f.read())
    except Exception as e:
        print(f"❌ Error reading README: {e}")


def main():
    """Main menu loop"""
    while True:
        print_menu()
        choice = input("\nSelect demo (0-5): ").strip()
        
        if choice == "0":
            print("\n👋 Goodbye!")
            break
        elif choice == "1":
            run_script("ollama_direct_test.py")
        elif choice == "2":
            run_script("ai_veterinary_demo.py")
        elif choice == "3":
            run_script("service_integration_test.py")
        elif choice == "4":
            run_script("end_to_end_workflow_test.py")
        elif choice == "5":
            show_readme()
        else:
            print("\n❌ Invalid choice. Please select 0-5.")
        
        if choice in ["1", "2", "3", "4"]:
            input("\n⏸️  Press Enter to continue...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
