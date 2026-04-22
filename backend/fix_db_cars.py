import sys
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Car, Team

def fix_cars():
    db = SessionLocal()
    print("Fixing car team IDs...")
    try:
        cars = db.query(Car).all()
        for car in cars:
            # Re-run the team matching logic but look for just "Red Bull" or others
            search_str = ""
            if car.manufacturer == "Red Bull":
                search_str = "Red Bull"
            elif car.manufacturer == "Mercedes":
                search_str = "Mercedes"
            elif car.manufacturer == "Ferrari":
                search_str = "Ferrari"
            elif car.manufacturer == "McLaren":
                search_str = "McLaren"
            elif car.manufacturer == "Aston Martin":
                search_str = "Aston Martin"
            elif car.manufacturer == "Alpine":
                search_str = "Alpine"
            elif car.manufacturer == "Renault": # Alpine is Renault
                search_str = "Alpine"
            elif car.manufacturer == "Alfa Romeo":
                search_str = "Alfa Romeo"
            elif car.manufacturer == "Alpha Tauri":
                search_str = "AlphaTauri"
            elif car.manufacturer == "Williams":
                search_str = "Williams"
            elif car.manufacturer == "Haas":
                search_str = "Haas"

            if search_str:
                team = db.query(Team).filter(Team.team_name.like(f"%{search_str}%")).first()
                if team:
                    car.team_id = team.team_id
                    print(f"Updated {car.model} ({car.manufacturer}) -> Team ID {team.team_id} ({team.team_name})")
                else:
                    print(f"Could not find team for {car.model} ({car.manufacturer}) with search '{search_str}'")
            
        db.commit()
        print("Done fixing car team IDs.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    fix_cars()
