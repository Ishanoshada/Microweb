import wifi
from microweb import MicroWeb

# Initialize MicroWeb with AP mode
app = MicroWeb(debug=True, ap={"ssid": "Portfolio_ESP32", "password": "portfolio123"})

# Portfolio data
portfolio_data = {
    "name": "John Developer",
    "title": "Full Stack Developer",
    "email": "john@example.com",
    "phone": "+1234567890",
    "location": "Tech City, TC",
    "about": "Passionate developer with 5+ years of experience in web development, IoT, and embedded systems.",
    "skills": ["Python", "JavaScript", "HTML/CSS", "React", "ESP32", "Arduino", "IoT Development"],
    "projects": [
        {
            "name": "Smart Home System",
            "description": "IoT-based home automation using ESP32 and mobile app",
            "tech": "ESP32, Python, React Native"
        },
        {
            "name": "Weather Station",
            "description": "Real-time weather monitoring with web dashboard",
            "tech": "ESP32, Sensors, Web API"
        },
        {
            "name": "Portfolio Website",
            "description": "Personal portfolio running on ESP32 microcontroller",
            "tech": "MicroPython, HTML, CSS"
        }
    ]
}

@app.route('/')
def home(req):
    return app.render_template('index.html', 
                             name=portfolio_data["name"],
                             title=portfolio_data["title"],
                             about=portfolio_data["about"])

@app.route('/about')
def about(req):
    skills_list = ", ".join(portfolio_data["skills"])
    return app.render_template('about.html',
                             name=portfolio_data["name"],
                             about=portfolio_data["about"],
                             skills=skills_list,
                             email=portfolio_data["email"],
                             phone=portfolio_data["phone"],
                             location=portfolio_data["location"])

@app.route('/projects')
def projects(req):
    projects_html = ""
    for project in portfolio_data["projects"]:
        projects_html += f"""
        <div class="project">
            <h3>{project["name"]}</h3>
            <p>{project["description"]}</p>
            <p><strong>Tech:</strong> {project["tech"]}</p>
        </div>
        """
    
    return app.render_template('projects.html',
                             name=portfolio_data["name"],
                             projects=projects_html)

@app.route('/contact')
def contact(req):
    return app.render_template('contact.html',
                             name=portfolio_data["name"],
                             email=portfolio_data["email"],
                             phone=portfolio_data["phone"],
                             location=portfolio_data["location"])

@app.route('/api/info', methods=['GET'])
def api_info(req):
    return app.json_response({
        "name": portfolio_data["name"],
        "title": portfolio_data["title"],
        "skills_count": len(portfolio_data["skills"]),
        "projects_count": len(portfolio_data["projects"]),
        "ip": wifi.get_ip()
    })

# Add static CSS file
app.add_static('/style.css', 'style.css')
app.add_static("/script.js","script.js")

# Run the server
app.run()
