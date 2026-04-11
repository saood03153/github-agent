import streamlit as st
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
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import base64
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="GitHub User Report",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Function to convert image to base64
def get_base64_image(image_path):
    """Convert image to base64 for embedding in CSS"""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return None

# Try to load robot background image
robot_image_path = Path("static/images/robot.png")
robot_loaded = False
robot_bg_url = ""

if robot_image_path.exists():
    robot_base64 = get_base64_image(robot_image_path)
    if robot_base64:
        robot_bg_url = f"data:image/png;base64,{robot_base64}"
        robot_loaded = True
    else:
        robot_loaded = False
else:
    robot_loaded = False

# Custom CSS matching the reference image colors
robot_css = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    * {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }}
    
    /* Animated background with robot image */
    .main::before {{
        content: '';
        position: fixed;
        top: 50%%;
        left: 50%%;
        width: 800px;
        height: 800px;
        background-image: url('{robot_bg_url}');
        background-size: contain;
        background-repeat: no-repeat;
        background-position: center;
        filter: blur(15px) brightness(1.2);
        opacity: 0.85;
        z-index: 0;
        animation: floatRobot 20s ease-in-out infinite;
        pointer-events: none;
        transform: translate(-50%%, -50%%);
    }}
    
    .main::after {{
        content: '';
        position: fixed;
        top: 30%%;
        right: 10%%;
        width: 400px;
        height: 400px;
        background: 
            radial-gradient(circle at 60%% 40%%, rgba(167, 139, 250, 0.3) 0%%, transparent 60%%),
            radial-gradient(circle at 30%% 60%%, rgba(244, 114, 182, 0.25) 0%%, transparent 60%%);
        filter: blur(60px);
        opacity: 0.5;
        z-index: 0;
        animation: floatBackground 25s ease-in-out infinite;
        pointer-events: none;
    }}
    
    @keyframes floatRobot {{
        0%%, 100%% {{ 
            transform: translate(-50%%, -50%%) scale(1) rotate(0deg);
        }}
        25%% {{ 
            transform: translate(-45%%, -55%%) scale(1.1) rotate(2deg);
        }}
        50%% {{ 
            transform: translate(-55%%, -45%%) scale(0.9) rotate(-2deg);
        }}
        75%% {{ 
            transform: translate(-48%%, -52%%) scale(1.05) rotate(1deg);
        }}
    }}
    
    @keyframes floatBackground {{
        0%%, 100%% {{ 
            transform: translate(0, 0) scale(1);
        }}
        25%% {{ 
            transform: translate(30px, -30px) scale(1.05);
        }}
        50%% {{ 
            transform: translate(-20px, 20px) scale(0.95);
        }}
        75%% {{ 
            transform: translate(20px, 15px) scale(1.02);
        }}
    }}
    
    /* Main container - Light gradient overlay */
    .main {{
        background: linear-gradient(135deg, rgba(224, 242, 254, 0.95) 0%%, rgba(186, 230, 253, 0.95) 50%%, rgba(125, 211, 252, 0.92) 100%%);
        position: relative;
        z-index: 1;
    }}
    
    .main > .block-container {{
        position: relative;
        z-index: 2;
    }}
    
    .block-container {{
        padding-top: 2rem;
        padding-bottom: 2rem;
    }}
    
    /* Header styling */
    .header-container {{
        background: linear-gradient(135deg, #667eea 0%%, #764ba2 100%%);
        padding: 25px 40px;
        border-radius: 20px;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
        margin-bottom: 30px;
    }}
    
    .main-title {{
        font-size: 28px;
        font-weight: 800;
        color: white;
        letter-spacing: 0.5px;
        margin: 0;
        text-transform: uppercase;
    }}
    
    .year-badge {{
        background: rgba(255, 255, 255, 0.25);
        backdrop-filter: blur(10px);
        color: #000000 !important;
        padding: 8px 20px;
        border-radius: 12px;
        font-weight: 700;
        font-size: 18px;
        border: 2px solid rgba(255, 255, 255, 0.3);
    }}
    
    /* 3D Card Effect with Glass-morphism */
    .stMetric, div[data-testid="metric-container"] {{
        background: rgba(255, 255, 255, 0.95) !important;
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        padding: 25px;
        border-radius: 18px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15), 
                    0 4px 8px rgba(0, 0, 0, 0.1),
                    inset 0 1px 0 rgba(255, 255, 255, 0.8);
        border: 1px solid rgba(102, 126, 234, 0.3);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
    }}
    
    .stMetric:hover, div[data-testid="metric-container"]:hover {{
        transform: translateY(-5px);
        box-shadow: 0 12px 48px rgba(102, 126, 234, 0.25),
                    0 6px 12px rgba(0, 0, 0, 0.15);
        background: rgba(255, 255, 255, 1) !important;
    }}
    
    .stMetric label {{
        color: #64748b !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    
    .stMetric [data-testid="stMetricValue"] {{
        color: #1e293b !important;
        font-size: 36px !important;
        font-weight: 800 !important;
    }}
    
    /* Profile card with 3D effect and glass-morphism */
    .profile-card {{
        background: rgba(255, 255, 255, 0.95) !important;
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        padding: 35px;
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15),
                    inset 0 1px 0 rgba(255, 255, 255, 0.8);
        margin-bottom: 25px;
        border: 1px solid rgba(102, 126, 234, 0.3);
    }}
    
    /* Analysis box with gradient */
    .analysis-box {{
        background: rgba(255, 255, 255, 0.95) !important;
        padding: 30px;
        border-radius: 18px;
        color: #1e293b;
        line-height: 1.8;
        margin: 20px 0;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.2);
        border: 2px solid rgba(102, 126, 234, 0.3);
    }}
    
    /* Buttons with gradient */
    .stButton button {{
        background: linear-gradient(135deg, #667eea 0%%, #764ba2 100%%);
        color: #1e293b !important;
        border: none;
        border-radius: 14px;
        padding: 16px 45px;
        font-size: 16px;
        font-weight: 700;
        transition: all 0.3s;
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
        border: 2px solid rgba(255, 255, 255, 0.1);
    }}
    
    .stButton button:hover {{
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.6);
        transform: translateY(-2px);
    }}
    
    /* Input with modern style - BLACK TEXT */
    .stTextInput input,
    .stTextInput > div > div > input,
    input[type="text"],
    textarea {{
        border-radius: 14px;
        border: 2px solid rgba(255, 255, 255, 0.2);
        padding: 16px 20px;
        font-size: 16px;
        background: rgba(255, 255, 255, 0.95) !important;
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        transition: all 0.3s;
    }}
    
    .stTextInput input:focus,
    .stTextInput > div > div > input:focus,
    input[type="text"]:focus {{
        border-color: #667eea;
        box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.2);
        background: white !important;
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
    }}
    
    .stTextInput input::placeholder,
    input[type="text"]::placeholder {{
        color: #94a3b8 !important;
        -webkit-text-fill-color: #94a3b8 !important;
    }}
    
    /* Chart containers with glass effect */
    div[data-testid="stPlotlyChart"] {{
        background: rgba(255, 255, 255, 0.95) !important;
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        padding: 20px;
        border-radius: 18px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15),
                    inset 0 1px 0 rgba(255, 255, 255, 0.8);
        border: 1px solid rgba(102, 126, 234, 0.3);
    }}
    
    /* Expander with glass-morphism */
    .streamlit-expanderHeader {{
        background: rgba(255, 255, 255, 0.95) !important;
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 14px;
        font-weight: 700;
        color: #1e293b;
        padding: 15px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(102, 126, 234, 0.3);
    }}
    
    /* Hide Streamlit branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    
    /* Repository item with modern card and glass effect */
    .repo-item {{
        background: rgba(255, 255, 255, 0.95) !important;
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        padding: 20px;
        border-radius: 14px;
        margin: 12px 0;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(102, 126, 234, 0.25);
        transition: all 0.3s;
    }}
    
    .repo-item:hover {{
        transform: translateX(5px);
        box-shadow: 0 6px 24px rgba(102, 126, 234, 0.2);
        border-left: 4px solid #667eea;
    }}
    
    .repo-name {{
        font-weight: 700;
        color: #1e293b;
        font-size: 17px;
        margin-bottom: 8px;
    }}
    
    .repo-desc {{
        color: #64748b;
        font-size: 14px;
        margin: 8px 0;
        line-height: 1.5;
    }}
    
    .repo-stats {{
        color: #94a3b8;
        font-size: 13px;
        margin-top: 12px;
        font-weight: 600;
    }}
    
    /* Follower cards */
    .follower-item {{
        background: rgba(255, 255, 255, 0.95) !important;
        padding: 15px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(102, 126, 234, 0.25);
        transition: all 0.3s;
    }}
    
    .follower-item:hover {{
        transform: translateY(-3px);
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.2);
    }}
    
    /* Section headers */
    h2, h3 {{
        color: #1e293b !important;
        font-weight: 700 !important;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }}
    
    /* Image styling */
    img {{
        border-radius: 12px;
    }}
    
    /* Divider styling */
    hr {{
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.3), transparent);
        margin: 30px 0;
    }}
    
    /* Info/Error messages */
    .stAlert {{
        background: white;
        border-radius: 12px;
        border-left: 4px solid #667eea;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
    }}
    
    /* Spinner */
    .stSpinner > div {{
        border-top-color: #667eea !important;
    }}

</style>
"""

st.markdown(robot_css, unsafe_allow_html=True)

load_dotenv()

# Initialize Groq LLM
@st.cache_resource
def get_llm():
    return ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model_name="llama-3.3-70b-versatile",
        temperature=0.7
    )

llm = get_llm()

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

# Build the graph
@st.cache_resource
def build_graph():
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
    return workflow.compile(checkpointer=memory)

graph = build_graph()

# Initialize session state
if 'analyzed' not in st.session_state:
    st.session_state.analyzed = False
if 'result' not in st.session_state:
    st.session_state.result = None

# Header
st.markdown("""
<div class="header-container" style="display: flex; justify-content: space-between; align-items: center;">
    <h1 class="main-title">🤖 GitHub User Report</h1>
    <div class="year-badge">2026</div>
</div>
""", unsafe_allow_html=True)

# Search section
col1, col2 = st.columns([4, 1])
with col1:
    username = st.text_input("", placeholder="Enter GitHub username...", label_visibility="collapsed", key="username_input")
with col2:
    analyze_btn = st.button("🔍 Analyze Profile", use_container_width=True)

# Analysis logic
if analyze_btn and username:
    with st.spinner("🤖 Analyzing GitHub profile with AI agent..."):
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
        
        st.session_state.result = result
        st.session_state.analyzed = True

# Display results
if st.session_state.analyzed and st.session_state.result:
    result = st.session_state.result
    data = result['github_data']
    
    if 'error' in data:
        st.error(f"❌ {data['error']}")
    else:
        # Profile Section
        st.markdown("---")
        st.markdown("<div class='profile-card'>", unsafe_allow_html=True)
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.image(data['profile']['avatar_url'], width=150)
        
        with col2:
            st.markdown(f"<h2 style='color: #1e293b !important; margin-bottom: 5px;'>{data['profile']['name']}</h2>", unsafe_allow_html=True)
            st.markdown(f"<p style='color: #64748b; font-size: 18px; margin-bottom: 15px;'>@{data['profile']['login']}</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='color: #475569; font-size: 15px; line-height: 1.6; margin-bottom: 20px;'>{data['profile']['bio']}</p>", unsafe_allow_html=True)
            
            detail_col1, detail_col2, detail_col3, detail_col4 = st.columns(4)
            with detail_col1:
                st.markdown(f"<div style='padding: 10px; background: linear-gradient(135deg, #667eea15 0%%, #764ba215 100%%); border-radius: 10px;'><strong style='color: #1e293b;'>🏢 Company</strong><br/><span style='color: #64748b;'>{data['profile']['company']}</span></div>", unsafe_allow_html=True)
            with detail_col2:
                st.markdown(f"<div style='padding: 10px; background: linear-gradient(135deg, #f093fb15 0%%, #f5576c15 100%%); border-radius: 10px;'><strong style='color: #1e293b;'>📍 Location</strong><br/><span style='color: #64748b;'>{data['profile']['location']}</span></div>", unsafe_allow_html=True)
            with detail_col3:
                st.markdown(f"<div style='padding: 10px; background: linear-gradient(135deg, #14b8a615 0%%, #059e6915 100%%); border-radius: 10px;'><strong style='color: #1e293b;'>📅 Account Age</strong><br/><span style='color: #64748b;'>{data['stats']['account_age_days']} days</span></div>", unsafe_allow_html=True)
            with detail_col4:
                st.markdown(f"<div style='padding: 10px; background: linear-gradient(135deg, #fb923c15 0%%, #f9731615 100%%); border-radius: 10px;'><strong style='color: #1e293b;'>📈 Repos/Year</strong><br/><span style='color: #64748b;'>{data['stats']['repos_per_year']}</span></div>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("---")
        
        # Statistics Dashboard
        st.subheader("📊 Profile Statistics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Followers", f"{data['profile']['followers']:,}")
        with col2:
            st.metric("Following", f"{data['profile']['following']:,}")
        with col3:
            st.metric("Public Repos", f"{data['profile']['public_repos']:,}")
        with col4:
            st.metric("Total Stars", f"{data['repositories']['total_stars']:,}")
        
        st.markdown("---")
        
        # Charts Row 1
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("💻 Programming Languages")
            if data['repositories']['languages']:
                # Sort languages by count
                sorted_langs = sorted(data['repositories']['languages'].items(), key=lambda x: x[1], reverse=True)[:5]
                
                fig = go.Figure(data=[go.Pie(
                    labels=[lang[0] for lang in sorted_langs],
                    values=[lang[1] for lang in sorted_langs],
                    hole=0.5,
                    marker=dict(
                        colors=['#a78bfa', '#f472b6', '#60a5fa', '#34d399', '#fb923c'],
                        line=dict(color='white', width=3)
                    )
                )])
                fig.update_layout(
                    showlegend=True,
                    height=300,
                    margin=dict(t=10, b=10, l=10, r=10),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12, color='#1e293b', family='Inter')
                )
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            else:
                st.info("No language data available")
        
        with col2:
            st.subheader("📈 Activity Overview")
            activity_data = {
                'Metric': ['Repos', 'Stars', 'Forks', 'Gists'],
                'Count': [
                    data['profile']['public_repos'],
                    data['repositories']['total_stars'],
                    data['repositories']['total_forks'],
                    data['profile']['public_gists']
                ]
            }
            fig = px.bar(
                activity_data,
                x='Metric',
                y='Count',
                color='Metric',
                color_discrete_sequence=['#667eea', '#764ba2', '#f093fb', '#f5576c']
            )
            fig.update_layout(
                showlegend=False,
                height=300,
                margin=dict(t=10, b=10, l=10, r=10),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(size=12, color='#1e293b', family='Inter'),
                yaxis=dict(gridcolor='rgba(0,0,0,0.05)'),
                xaxis=dict(showgrid=False)
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        st.markdown("---")
        
        # Charts Row 2
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎯 Engagement Metrics")
            engagement_data = {
                'Type': ['Followers', 'Following'],
                'Count': [data['profile']['followers'], data['profile']['following']]
            }
            fig = go.Figure(data=[go.Pie(
                labels=engagement_data['Type'],
                values=engagement_data['Count'],
                marker=dict(
                    colors=['#14b8a6', '#f472b6'],
                    line=dict(color='white', width=3)
                )
            )])
            fig.update_layout(
                showlegend=True,
                height=300,
                margin=dict(t=10, b=10, l=10, r=10),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(size=12, color='#1e293b', family='Inter')
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        with col2:
            st.subheader("⭐ Top Repositories")
            for repo in data['repositories']['top_repos'][:5]:
                st.markdown(f"""
                <div class="repo-item">
                    <div class="repo-name">{repo['name']}</div>
                    <div class="repo-desc">{repo['description']}</div>
                    <div class="repo-stats">
                        ⭐ {repo['stars']} | 🔀 {repo['forks']} | 💻 {repo['language']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Show All Repositories button
            if len(data['repositories']['top_repos']) > 5:
                with st.expander(f"📂 View All {len(data['repositories']['top_repos'])} Repositories"):
                    for repo in data['repositories']['top_repos']:
                        repo_url = f"https://github.com/{username}/{repo['name']}"
                        st.markdown(f"""
                        <div style='background: white; padding: 12px; border-radius: 10px; margin-bottom: 10px; border-left: 4px solid #667eea;'>
                            <div style='font-size: 16px; font-weight: 600; color: #1e293b; margin-bottom: 5px;'>
                                <a href='{repo_url}' target='_blank' style='text-decoration: none; color: #667eea;'>
                                    🔗 {repo['name']}
                                </a>
                            </div>
                            <div style='font-size: 13px; color: #64748b; margin-bottom: 8px;'>{repo['description'] if repo['description'] else 'No description'}</div>
                            <div style='font-size: 12px; color: #94a3b8;'>
                                ⭐ {repo['stars']} | 🔀 {repo['forks']} | 💻 {repo['language']}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Followers Section
        st.subheader("👥 Recent Followers")
        if data['followers']:
            cols = st.columns(6)
            for idx, follower in enumerate(data['followers'][:12]):
                with cols[idx % 6]:
                    st.markdown(f"""
                    <div style='background: white; padding: 15px; border-radius: 12px; text-align: center; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08); transition: all 0.3s;'>
                        <img src='{follower['avatar_url']}' style='width: 70px; height: 70px; border-radius: 50%; border: 3px solid #667eea; margin-bottom: 8px;' />
                        <div style='font-size: 12px; color: #1e293b; font-weight: 600;'>
                            <a href='{follower['url']}' target='_blank' style='text-decoration: none; color: #667eea;'>@{follower['login']}</a>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No followers yet")
        
        st.markdown("---")
        
        # AI Analysis
        st.subheader("🤖 AI-Powered Analysis")
        st.markdown(f"""
        <div class="analysis-box">
            {result['analysis']}
        </div>
        """, unsafe_allow_html=True)
        
        # LangGraph Visualization
        st.markdown("---")
        with st.expander("🔄 View Agent Graph Flow"):
            st.info("**LangGraph Agent Flow:**\n\n1️⃣ **Fetch Node** → Retrieves GitHub API data\n\n2️⃣ **Analyze Node** → AI analysis using Groq LLM\n\n3️⃣ **Memory Saver** → Stores analysis for future quick retrieval")
            st.code(f"""
Thread ID: {username}
Nodes Executed: fetch → analyze
Memory Saved: ✓
Model: Llama 3.1 70B
            """, language="text")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #718096; padding: 20px;">
    Built with ❤️ using LangGraph, Groq AI, and Streamlit | All data from GitHub Public API
</div>
""", unsafe_allow_html=True)
