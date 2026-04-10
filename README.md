# GitHub User Report Agent 🚀

A beautiful and intelligent GitHub profile analyzer built with **LangGraph**, **Groq API**, **Streamlit**, and a stunning UI/UX design inspired by modern analytics dashboards.

## ✨ Features

- 🤖 **AI-Powered Analysis** - Uses Groq's LLM to provide intelligent insights about GitHub profiles
- 📊 **Beautiful Visualizations** - Interactive Plotly charts showing languages, activity, and engagement
- 💾 **Memory Persistence** - LangGraph memory saver stores analysis history
- 🎨 **Modern UI/UX** - Elegant Streamlit design with custom CSS and responsive layout
- 📈 **Comprehensive Data** - Fetches followers, repositories, stars, forks, and more
- ⚡ **Real-time Analysis** - Fast data fetching and processing

## 🎯 What It Does

Enter any GitHub username and get:

1. **Profile Overview** - Avatar, bio, location, company, and account details
2. **Statistics Dashboard** - Followers, repos, stars, and engagement metrics
3. **Language Distribution** - Visual breakdown of programming languages used
4. **Top Repositories** - Your most popular projects with stars and forks
5. **Follower Insights** - See who's following the user
6. **AI Analysis** - Intelligent insights about the developer's expertise and activity
7. **Graph Visualization** - See the LangGraph agent flow in action

## 🛠️ Technologies Used

- **Frontend Framework**: Streamlit
- **AI Agent**: LangGraph with memory persistence
- **LLM**: Groq API (Llama 3.3 70B)
- **Data Source**: GitHub REST API
- **Charts**: Plotly Express & Plotly Graph Objects
- **Styling**: Custom CSS with modern gradients
- **Frontend**: HTML5, CSS3, JavaScript
- **Charts**: Chart.js
- **Styling**: Custom CSS with modern gradients and animations

## 📋 Prerequisites

- Python 3.8+
- Groq API key ([Get one here](https://console.groq.com/keys))
- Internet connection for GitHub API access

## 🚀 Installation

1. **Clone or navigate to the project directory**:
   ```bash
   cd "e:\GitHub Agent"
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   - Copy `.env.example` to `.env`
   - Add your Groq API key:
   ```
   GROQ_API_KEY=your_actual_groq_api_key
   ```

4. **Run the application**:
   ```bash
   python app.py
   ```

5. **Open your browser**:
   Navigate to `http://localhost:5000`

## 📖 Usage

1. Enter a GitHub username in the search box
2. Click "Analyze Profile" button
3. Wait for the AI agent to fetch and analyze the data
4. Explore the beautiful dashboard with:
   - Profile statistics
   - Programming language breakdown
   - Activity metrics
   - Top repositories
   - Recent followers
   - AI-generated insights

## 🎨 Design Features

The UI features a beautiful color palette inspired by modern analytics:
- Primary: `#ed8a63` (Warm Orange)
- Secondary: `#e17055` (Coral)
- Accents: `#fdcb9e`, `#fce8df` (Peach tones)
- Background gradients for depth
- Custom Streamlit components with CSS
- Responsive grid layouts
- Interactive Plotly charts

## 🔧 How It Works

### LangGraph Agent Architecture

1. **Fetch Node** - Retrieves GitHub data via REST API
2. **Analyze Node** - Uses Groq LLM to generate insights
3. **Memory Saver** - Persists analysis history per username
4. **Conditional Edges** - Smart flow control based on data availability

```python
workflow = StateGraph(AgentState)
workflow.add_node("fetch", fetch_data_node)
workflow.add_node("analyze", analyze_data_node)
workflow.set_entry_point("fetch")
graph = workflow.compile(checkpointer=memory)
```

### Data Flow

```
User Input → Streamlit → LangGraph Agent → GitHub API
                ↓
        Groq AI Analysis
                ↓
        Memory Saved → Streamlit UI → Beautiful Visualization
```

## 🌟 Key Components

### Streamlit App (streamlit_app.py)
- Beautiful Streamlit interface with custom CSS
- LangGraph state machine
- Groq LLM integration  
- GitHub API client
- Memory persistence (MemorySaver)
- Interactive Plotly visualizations
- Real-time data fetching and analysis
- Session state management

## 🔒 Security Notes

- Never commit your `.env` file with real API keys
- Keep your Groq API key secret
- GitHub API has rate limits (60 requests/hour unauthenticated)
- The included API key in `.env.example` is for demo purposes

## 🎯 Future Enhancements

- [ ] GitHub authentication for higher rate limits
- [ ] Export reports as PDF
- [ ] Compare multiple users side-by-side
- [ ] Historical trend analysis
- [ ] More chart types and visualizations
- [ ] Dark mode toggle
- [ ] Repository contribution graphs
- [ ] Activity heatmap

## 📝 License

This project is open source and available for educational purposes.

## 🤝 Contributing

Feel free to fork, modify, and use this project for your own purposes!

## 💡 Tips

- Try analyzing popular GitHub users like `torvalds`, `gaearon`, or `tj`
- The AI analysis is powered by Groq's fast LLM inference
- Memory saver means returning to the same username loads faster
- All data is public GitHub information

---

**Built with ❤️ using LangGraph and Groq AI**
