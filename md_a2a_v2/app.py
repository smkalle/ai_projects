from dotenv import load_dotenv
from graph import app

def main():
    load_dotenv()
    query = "What documentaries exist on renewable energy?"
    state = {"messages": [{"role": "user", "content": query}]}
    result = app.invoke(state)
    print(result)

if __name__ == "__main__":
    main()
