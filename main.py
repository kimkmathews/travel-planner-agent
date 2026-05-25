from dotenv import load_dotenv
load_dotenv()

import sys
from src.session.manager import TravelPlannerSession


def print_itinerary_summary(result: dict):
    """Print a clean summary of the structured itinerary."""
    itinerary = result.get("structured_itinerary")
    if not itinerary:
        return

    print(f"\n{'='*60}")
    print(f"🗺️  {itinerary.trip_title}")
    print(f"{'='*60}")
    print(f"📅 {itinerary.duration_days} days | {itinerary.travel_month}")
    print(f"👨‍👩‍👦 {itinerary.party}")
    print(f"🌤️  {itinerary.weather_summary}")
    print(f"\n💰 Cost Summary:")
    cb = itinerary.cost_breakdown
    print(f"   Flights:        ₹{cb.flights_inr:>8,}")
    print(f"   Accommodation:  ₹{cb.accommodation_inr:>8,}")
    print(f"   Meals:          ₹{cb.meals_inr:>8,}")
    print(f"   Activities:     ₹{cb.activities_inr:>8,}")
    print(f"   Transport/Misc: ₹{cb.transport_misc_inr:>8,}")
    print(f"   {'─'*28}")
    print(f"   TOTAL:          ₹{cb.total_inr:>8,}  {'✅ Under budget' if cb.is_within_budget else '❌ Over budget'}")

    if result.get("warnings"):
        print(f"\n⚠️  Data quality warnings:")
        for w in result["warnings"]:
            print(f"   {w}")

    print(f"\n📎 Sources consulted: {len(itinerary.data_sources)}")
    print(f"{'='*60}\n")


def main():
    print("🧳 Travel Planner AI — Chat Interface")
    print("   Type your travel query to begin, or 'quit' to exit.")
    print("   After the first itinerary, ask follow-up questions freely.\n")

    session = None

    # Optional: restore existing session
    if len(sys.argv) > 1 and sys.argv[1].startswith("--session="):
        existing_id = sys.argv[1].split("=")[1]
        session = TravelPlannerSession.restore(existing_id)
        print(f"   Restored session {existing_id}. Continue your conversation.\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\nGoodbye! 👋")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "bye"):
            print("Goodbye! 👋")
            break
        if user_input.lower() == "new session":
            session = None
            print("✨ Starting new session.\n")
            continue

        # Create session on first message
        if session is None:
            session = TravelPlannerSession()
            print(f"   (Save your session ID to resume later: {session.thread_id})\n")

        result = session.chat(user_input, stream=True)
        print_itinerary_summary(result)


if __name__ == "__main__":
    main()