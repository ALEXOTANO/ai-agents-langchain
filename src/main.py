"""
CLI Entry Point for LangGraph Agents Demo

Usage:
    python -m src.main triage "El servicio de pagos está lento"
    python -m src.main fixer "El servicio de pagos está lento, arréglalo"
"""
import argparse
import sys
from dotenv import load_dotenv

# Load env vars
load_dotenv()

from src.agents.devops_agent import run_devops_agent
from src.agents.triage_chain import run_triage_agent


def main():
    parser = argparse.ArgumentParser(
        description="LangGraph Incident Response Demo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m src.main triage "El servicio de pagos está lento"
  python -m src.main fixer "Hay alta latencia en el servicio de pagos, soluciónalo"
        """
    )
    
    parser.add_argument(
        "mode",
        choices=["triage", "fixer"],
        help="Mode to run: 'triage' or 'fixer' "
    )
    
    parser.add_argument(
        "input",
        help="Input for the agent (incident description)"
    )
    
    parser.add_argument(
        "--local",
        action="store_true",
        help="Use Ollama (Mistral) locally instead of OpenAI"
    )
    
    args = parser.parse_args()
    
    print(f"\n{'='*60}")
    print(f"🤖 Running Mode: {args.mode.upper()}")
    print(f"📝 Input: {args.input}")
    print(f"{'='*60}\n")
    
    try:
        if args.mode == "triage":
            result = run_triage_agent(args.input)
        elif args.mode == "fixer":
            result = run_devops_agent(args.input, args.local)
        
        print("\n📋 Final Report / Response:")
        print("-" * 40)
        print(result)
        print("-" * 40)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
