from livekit.agents import function_tool, RunContext
import webbrowser

@function_tool
async def open_url(url: str, context: RunContext) -> str:
    """
    Opens a URL in the user's default web browser.
    Useful for showing documentation, resources, or references during interviews.
    
    Args:
        url: The URL to open in the browser
        
    Returns:
        A confirmation message
    """
    try:
        webbrowser.open(url)
        return f"Opened {url} in your web browser."
    except Exception as e:
        return f"Failed to open {url}. Error: {str(e)}"


@function_tool
async def get_career_resources(topic: str, context: RunContext) -> str:
    """
    Provides career resources and guidance based on the requested topic.
    Useful during career advisory sessions.
    
    Args:
        topic: The career topic to get resources for (e.g., "resume tips", "interview prep", "skill development")
        
    Returns:
        Relevant career resources and guidance
    """
    resources = {
        "resume tips": """
        Key Resume Tips:
        1. Keep it concise (1-2 pages)
        2. Use action verbs and quantify achievements
        3. Tailor to each job application
        4. Include relevant technical skills
        5. Highlight impact and results, not just duties
        """,
        
        "interview prep": """
        Interview Preparation Guide:
        1. Research the company thoroughly
        2. Practice common technical and behavioral questions
        3. Prepare STAR method examples
        4. Review your resume and be ready to discuss everything
        5. Prepare thoughtful questions for the interviewer
        6. Practice coding problems on platforms like LeetCode
        """,
        
        "skill development": """
        Skill Development Strategies:
        1. Identify in-demand skills in your target role
        2. Use online platforms: Coursera, Udemy, YouTube
        3. Build projects to apply new skills
        4. Contribute to open source
        5. Join developer communities
        6. Stay updated with industry trends
        """,
        
        "networking": """
        Networking Tips:
        1. Attend tech meetups and conferences
        2. Be active on LinkedIn
        3. Engage in online communities (Reddit, Discord, Stack Overflow)
        4. Reach out to professionals for informational interviews
        5. Maintain relationships over time
        """,
        
        "job search": """
        Effective Job Search Strategies:
        1. Use multiple job boards (LinkedIn, Indeed, Glassdoor)
        2. Apply directly on company websites
        3. Network and get referrals
        4. Customize your application for each role
        5. Follow up on applications
        6. Track your applications
        """
    }
    
    topic_lower = topic.lower()
    for key, value in resources.items():
        if key in topic_lower:
            return value
    
    return f"""
    I don't have specific resources for '{topic}' yet, but I can help with:
    - Resume tips
    - Interview preparation
    - Skill development
    - Networking strategies
    - Job search advice
    
    What would you like to know more about?
    """
