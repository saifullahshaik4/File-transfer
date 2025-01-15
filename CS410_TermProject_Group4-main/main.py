from dotenv import load_dotenv
from menu import menu

def main():
    try: 
        load_dotenv()
        menu()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
