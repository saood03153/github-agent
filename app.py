from flask import Flask, render_template, request, jsonify
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from typing import TypedDict, Annotated
import requests
import os
from dotenv import load_dotenv
from datetime import datetime
import operator

load_dotenv()

app = Flask(__name__)

# Initialize Groq LLM
llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.3-70b-versatile",
    temperature=0.7
)

# Define the state for our agent
class AgentState(TypedDict):
    username: str
    github_data: dict
    analysis: str
    messages: Annotated[list, operator.add]
    processed: bool

# Initialize memory saver
memory = MemorySaver()

def fetch_github_data(username):
    """Fetch GitHub public data for a user"""
    try:
        # User data
        user_response = requests.get(f"https://api.github.com/users/{username}")
        if user_response.status_code != 200:
            return {"error": "User not found"}
        
        user_data = user_response.json()
        
        # Repositories data
        repos_response = requests.get(f"https://api.github.com/users/{username}/repos?per_page=100")
        repos_data = repos_response.json() if repos_response.status_code == 200 else []
        
        # Followers
        followers_response = requests.get(f"https://api.github.com/users/{username}/followers?per_page=100")
        followers_data = followers_response.json() if followers_response.status_code == 200 else []
        
        # Following
        following_response = requests.get(f"https://api.github.com/users/{username}/following?per_page=100")
        following_data = following_response.json() if following_response.status_code == 200 else []
        
        # Process repository data
        languages = {}
        stars_total = 0
        forks_total = 0
        repo_list = []
        
        for repo in repos_data:
            if repo.get('language'):
                languages[repo['language']] = languages.get(repo['language'], 0) + 1
            stars_total += repo.get('stargazers_count', 0)
            forks_total += repo.get('forks_count', 0)
            repo_list.append({
                'name': repo['name'],
                'description': repo.get('description', 'No description'),
                'stars': repo.get('stargazers_count', 0),
                'forks': repo.get('forks_count', 0),
                'language': repo.get('language', 'Unknown'),
                'url': repo['html_url']
            })
        
        # Sort repos by stars
        repo_list.sort(key=lambda x: x['stars'], reverse=True)
        
        return {
            'profile': {
                'login': user_data['login'],
                'name': user_data.get('name', user_data['login']),
                'avatar_url': user_data['avatar_url'],
                'bio': user_data.get('bio', 'No bio available'),
                'company': user_data.get('company', 'N/A'),
                'location': user_data.get('location', 'N/A'),
                'email': user_data.get('email', 'N/A'),
                'blog': user_data.get('blog', 'N/A'),
                'twitter_username': user_data.get('twitter_username', 'N/A'),
                'public_repos': user_data['public_repos'],
                'public_gists': user_data['public_gists'],
                'followers': user_data['followers'],
                'following': user_data['following'],
                'created_at': user_data['created_at'],
                'updated_at': user_data['updated_at']
            },
            'repositories': {
                'total': len(repos_data),
                'total_stars': stars_total,
                'total_forks': forks_total,
                'languages': languages,
                'top_repos': repo_list[:10]
            },
            'followers': [{'login': f['login'], 'avatar_url': f['avatar_url'], 'url': f['html_url']} for f in followers_data[:20]],
            'following': [{'login': f['login'], 'avatar_url': f['avatar_url'], 'url': f['html_url']} for f in following_data[:20]],
            'stats': {
                'account_age_days': (datetime.now() - datetime.strptime(user_data['created_at'], '%Y-%m-%dT%H:%M:%SZ')).days,
                'repos_per_year': round(len(repos_data) / max(1, (datetime.now() - datetime.strptime(user_data['created_at'], '%Y-%m-%dT%H:%M:%SZ')).days / 365), 2)
            }
        }
    except Exception as e:
        return {"error": str(e)}

def fetch_data_node(state: AgentState) -> AgentState:
    """Node to fetch GitHub data"""
    username = state['username']
    github_data = fetch_github_data(username)
    
    return {
        **state,
        'github_data': github_data,
        'messages': [HumanMessage(content=f"Fetched data for user: {username}")]
    }

def analyze_data_node(state: AgentState) -> AgentState:
    """Node to analyze GitHub data using Groq"""
    github_data = state['github_data']
    
    if 'error' in github_data:
        return {
            **state,
            'analysis': f"Error: {github_data['error']}",
            'processed': True
        }
    
    # Create analysis prompt
    prompt = f"""Analyze this GitHub user profile and provide insights:

User: {github_data['profile']['name']} (@{github_data['profile']['login']})
Bio: {github_data['profile']['bio']}
Location: {github_data['profile']['location']}
Company: {github_data['profile']['company']}

Statistics:
- Followers: {github_data['profile']['followers']}
- Following: {github_data['profile']['following']}
- Public Repositories: {github_data['profile']['public_repos']}
- Total Stars: {github_data['repositories']['total_stars']}
- Total Forks: {github_data['repositories']['total_forks']}
- Account Age: {github_data['stats']['account_age_days']} days
- Repos per Year: {github_data['stats']['repos_per_year']}

Top Languages: {', '.join([f'{lang} ({count})' for lang, count in sorted(github_data['repositories']['languages'].items(), key=lambda x: x[1], reverse=True)[:5]])}

Top Repository: {github_data['repositories']['top_repos'][0]['name'] if github_data['repositories']['top_repos'] else 'None'} ({github_data['repositories']['top_repos'][0]['stars'] if github_data['repositories']['top_repos'] else 0} stars)

Provide a brief, insightful analysis of this developer's profile, including their expertise, activity level, and community engagement."""
    
    messages = [
        SystemMessage(content="You are a GitHub profile analyzer. Provide concise, insightful analysis of developer profiles."),
        HumanMessage(content=prompt)
    ]
    
    response = llm.invoke(messages)
    
    return {
        **state,
        'analysis': response.content,
        'messages': state['messages'] + [response],
        'processed': True
    }

def should_continue(state: AgentState) -> str:
    """Determine if we should continue processing"""
    if state.get('processed', False):
        return "end"
    return "analyze"

# Build the graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("fetch", fetch_data_node)
workflow.add_node("analyze", analyze_data_node)

# Add edges
workflow.set_entry_point("fetch")
workflow.add_conditional_edges(
    "fetch",
    lambda state: "analyze" if 'error' not in state['github_data'] else "analyze"
)
workflow.add_edge("analyze", END)

# Compile the graph with memory
graph = workflow.compile(checkpointer=memory)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    username = data.get('username', '').strip()
    
    if not username:
        return jsonify({'error': 'Username is required'}), 400
    
    # Create initial state
    initial_state = {
        'username': username,
        'github_data': {},
        'analysis': '',
        'messages': [],
        'processed': False
    }
    
    # Run the graph with memory
    config = {"configurable": {"thread_id": username}}
    result = graph.invoke(initial_state, config)
    
    return jsonify({
        'username': username,
        'data': result['github_data'],
        'analysis': result['analysis']
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
