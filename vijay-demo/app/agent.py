# Multi-Agent Teacher Assistant System with ShikshaAI - Firestore Edition

import datetime
import json
from zoneinfo import ZoneInfo
from typing import Dict, List, Optional, Any
import logging

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

import os
import google.auth
from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from app.mcp_service.capabilities import get_enhanced_capabilities

# MCP Service Integration - World Bank and Google Trends data
from app.mcp_service import (
    get_india_education_stats,
    get_trending_education_topics,
    get_teaching_insights,
    compare_country_education,
    search_education_indicator
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_, project_id = google.auth.default()
os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"

# ============================================
# FIRESTORE DATABASE SERVICE LAYER
# ============================================

class FirestoreService:
    """Firestore database service for all persistence operations"""
    
    def __init__(self):
        """Initialize Firestore client"""
        try:
            self.db = firestore.Client()
            self.initialized = True
            logger.info("✅ Firestore connected successfully")
        except Exception as e:
            logger.error(f"❌ Firestore connection failed: {e}")
            self.initialized = False
            raise
    
    # ============================================
    # GENERIC CRUD OPERATIONS
    # ============================================
    
    def create_document(self, collection: str, data: Dict, doc_id: Optional[str] = None) -> str:
        """Create a document in specified collection"""
        try:
            doc_ref = self.db.collection(collection).document(doc_id) if doc_id else self.db.collection(collection).document()
            data['created_at'] = datetime.datetime.now(ZoneInfo("Asia/Kolkata")).isoformat()
            data['updated_at'] = datetime.datetime.now(ZoneInfo("Asia/Kolkata")).isoformat()
            doc_ref.set(data)
            logger.info(f"✅ Created document in {collection} with ID: {doc_ref.id}")
            return doc_ref.id
        except Exception as e:
            logger.error(f"❌ Failed to create document in {collection}: {e}")
            raise
    
    def get_document(self, collection: str, doc_id: str) -> Optional[Dict]:
        """Retrieve a document by ID"""
        try:
            doc_ref = self.db.collection(collection).document(doc_id)
            doc = doc_ref.get()
            if doc.exists:
                data = doc.to_dict()
                data['id'] = doc.id
                return data
            return None
        except Exception as e:
            logger.error(f"❌ Failed to get document {doc_id} from {collection}: {e}")
            raise
    
    def update_document(self, collection: str, doc_id: str, data: Dict) -> bool:
        """Update a document"""
        try:
            data['updated_at'] = datetime.datetime.now(ZoneInfo("Asia/Kolkata")).isoformat()
            doc_ref = self.db.collection(collection).document(doc_id)
            doc_ref.update(data)
            logger.info(f"✅ Updated document {doc_id} in {collection}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to update document {doc_id}: {e}")
            return False
    
    def delete_document(self, collection: str, doc_id: str) -> bool:
        """Delete a document"""
        try:
            self.db.collection(collection).document(doc_id).delete()
            logger.info(f"✅ Deleted document {doc_id} from {collection}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to delete document {doc_id}: {e}")
            return False
    
    def query_documents(self, collection: str, filters: List[tuple] = None, limit: int = 100) -> List[Dict]:
        """Query documents with optional filters"""
        try:
            query = self.db.collection(collection)
            
            if filters:
                for field, op, value in filters:
                    query = query.where(filter=FieldFilter(field, op, value))
            
            docs = query.limit(limit).stream()
            results = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                results.append(data)
            
            return results
        except Exception as e:
            logger.error(f"❌ Failed to query {collection}: {e}")
            return []
    
    # ============================================
    # TASK-SPECIFIC OPERATIONS
    # ============================================
    
    def save_task(self, task: Dict) -> Dict:
        """Save a task to Firestore"""
        task['type'] = task.get('type', 'task') 
        task['completed'] = task.get('completed', False)
        task_id = self.create_document('tasks', task)
        task['id'] = task_id
        return task
    
    def get_tasks(self, include_completed: bool = False) -> List[Dict]:
        """Retrieve tasks with optional filtering"""
        if include_completed:
            return self.query_documents('tasks')
        else:
            return self.query_documents('tasks', [('completed', '==', False)])
    
    def update_task(self, task_id: str, updates: Dict) -> Optional[Dict]:
        """Update a task"""
        if self.update_document('tasks', task_id, updates):
            return self.get_document('tasks', task_id)
        return None
    
    def delete_task(self, task_id: str) -> bool:
        """Delete a task"""
        return self.delete_document('tasks', task_id)
    
    def delete_all_tasks(self, include_completed: bool = False) -> int:
        """Delete all tasks, optionally including completed ones"""
        tasks = self.get_tasks(include_completed=True) if include_completed else self.get_tasks(include_completed=False)
        count = 0
        for task in tasks:
            if self.delete_task(task['id']):
                count += 1
        return count
    
    # ============================================
    # ASSIGNMENT-SPECIFIC OPERATIONS
    # ============================================
    
    def save_assignment(self, assignment: Dict) -> Dict:
        """Save an assignment to Firestore"""
        assignment['type'] = 'assignment'
        assignment_id = self.create_document('assignments', assignment)
        assignment['id'] = assignment_id
        return assignment
    
    def get_assignments(self, course: Optional[str] = None) -> List[Dict]:
        """Retrieve assignments with optional course filter"""
        if course:
            return self.query_documents('assignments', [('course', '==', course)])
        else:
            return self.query_documents('assignments')
    
    def delete_assignment(self, assignment_id: str) -> bool:
        """Delete an assignment"""
        return self.delete_document('assignments', assignment_id)
    
    # ============================================
    # NOTE-SPECIFIC OPERATIONS
    # ============================================
    
    def save_note(self, note: Dict) -> Dict:
        """Save a note to Firestore"""
        note['type'] = 'note'
        note_id = self.create_document('notes', note)
        note['id'] = note_id
        return note
    
    def search_notes(self, query: str) -> List[Dict]:
        """Search notes by keyword in title or content"""
        # Firestore doesn't support full-text search natively
        # We'll retrieve all and filter (for POC)
        # For production, consider using Firestore + Algolia or Elasticsearch
        all_notes = self.query_documents('notes')
        results = []
        for note in all_notes:
            if (query.lower() in note.get('title', '').lower() or 
                query.lower() in note.get('content', '').lower()):
                results.append(note)
        return results
    
    def delete_note(self, note_id: str) -> bool:
        """Delete a note"""
        return self.delete_document('notes', note_id)
    
    # ============================================
    # LESSON-SPECIFIC OPERATIONS
    # ============================================
    
    def save_lesson(self, lesson: Dict) -> Dict:
        """Save a lesson to Firestore"""
        lesson['type'] = 'lesson'
        lesson_id = self.create_document('lesson_plans', lesson)
        lesson['id'] = lesson_id
        return lesson
    
    def get_lessons(self, subject: Optional[str] = None, grade: Optional[int] = None) -> List[Dict]:
        """Retrieve lessons with optional filters"""
        filters = []
        if subject:
            filters.append(('subject', '==', subject))
        if grade:
            filters.append(('grade', '==', grade))
        
        if filters:
            return self.query_documents('lesson_plans', filters)
        else:
            return self.query_documents('lesson_plans')
    
    def search_lessons(self, keyword: str) -> List[Dict]:
        """Search lessons by keyword in topic or explanation"""
        all_lessons = self.query_documents('lesson_plans')
        results = []
        for lesson in all_lessons:
            if (keyword.lower() in lesson.get('topic', '').lower() or 
                keyword.lower() in lesson.get('explanation', '').lower() or
                keyword.lower() in lesson.get('full_content', '').lower()):
                results.append(lesson)
        return results
    
    def get_lesson_stats(self) -> Dict:
        """Get lesson statistics"""
        all_lessons = self.query_documents('lesson_plans')
        
        stats = {
            'total_lessons': len(all_lessons),
            'by_subject': {},
            'by_grade': {},
            'by_language': {}
        }
        
        for lesson in all_lessons:
            subject = lesson.get('subject', 'Unknown')
            stats['by_subject'][subject] = stats['by_subject'].get(subject, 0) + 1
            
            grade = lesson.get('grade', 'Unknown')
            grade_key = "MSc" if grade == 16 else str(grade)
            stats['by_grade'][grade_key] = stats['by_grade'].get(grade_key, 0) + 1
            
            language = lesson.get('language', 'Unknown')
            stats['by_language'][language] = stats['by_language'].get(language, 0) + 1
        
        return stats
    
    def clear_all_data(self) -> None:
        """Clear all data from all collections (use with caution)"""
        collections = ['tasks', 'assignments', 'notes', 'lesson_plans']
        for collection in collections:
            docs = self.query_documents(collection)
            for doc in docs:
                self.delete_document(collection, doc['id'])
        logger.info("🗑️ All data cleared from Firestore")


# Initialize Firestore service
db = FirestoreService()

# ============================================
# STANDALONE TOOL FUNCTIONS
# ============================================

def read_lesson_plan(lesson_id: str) -> str:
    """Read the complete content of a specific lesson by its ID."""
    lesson = db.get_document('lesson_plans', lesson_id)
    
    if not lesson:
        return f"❌ Lesson with ID {lesson_id} not found."
    
    # Check if this is an old lesson that only has metadata, or a new one with full content
    content = lesson.get('full_content')
    if not content:
        content = "⚠️ This is an old lesson. Only metadata was saved, the actual content is missing. Please generate a new one."
        
    return f"""
    📚 **LESSON: {lesson.get('topic', 'Unknown')}**
    Subject: {lesson.get('subject')} | Grade: {lesson.get('grade')} | Language: {lesson.get('language')}
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    {content}
    """

def show_data_stats() -> str:
    """Show statistics about stored data."""
    assignments = db.get_assignments()
    all_collection_items = db.get_tasks(include_completed=True)
    
    actual_tasks = [t for t in all_collection_items if t.get('type') == 'task']
    calendar_events = [t for t in all_collection_items if t.get('type') in ['office_hours', 'meeting']]
    
    notes = db.query_documents('notes')
    lessons = db.query_documents('lesson_plans')
    
    pending_tasks = [t for t in actual_tasks if not t.get('completed', False)]
    completed_tasks = [t for t in actual_tasks if t.get('completed', False)]
    
    return f"""
    **📊 DATABASE STATISTICS (FIRESTORE):**

    - **📋 Assignments:** {len(assignments)}
    - **✅ Pending Tasks:** {len(pending_tasks)}
    - **✓ Completed Tasks:** {len(completed_tasks)}
    - **📅 Calendar Events:** {len(calendar_events)}
    - **📝 Notes:** {len(notes)}
    - **📚 Lessons:** {len(lessons)}

    *💾 Storage: Google Cloud Firestore*
    """

def clear_all_data() -> str:
    """Clear all data from the database (use with caution)."""
    db.clear_all_data()
    return "🗑️ All data has been cleared from Firestore."

# ============================================
# SUB-AGENT 1: TEACHING AGENT
# ============================================

def create_assignment(course: str, title: str, due_date: str, points: int = 100) -> str:
    """Create a new assignment for a course."""
    assignment = {
        "course": course,
        "title": title,
        "due_date": due_date,
        "points": points,
        "status": "pending"
    }
    saved = db.save_assignment(assignment)
    return f"✅ Assignment '{title}' created for {course}, due {due_date} ({points} points). Assignment ID: {saved['id']}"

def list_assignments(course: Optional[str] = None) -> str:
    """List all assignments, optionally filtered by course."""
    assignments = db.get_assignments(course)
    if not assignments:
        return "📭 No assignments found."
    
    result = "📋 Assignments:\n"
    for a in assignments:
        result += f"  • {a['course']}: {a['title']} - Due {a['due_date']} ({a['points']} pts) [ID: {a['id']}]\n"
    return result

def delete_assignment(assignment_id: str) -> str:
    """Delete an assignment by ID."""
    if db.delete_assignment(assignment_id):
        return f"🗑️ Assignment ID {assignment_id} has been deleted."
    return f"❌ Assignment with ID {assignment_id} not found."

def grade_submission(assignment_id: str, student_name: str, submission_text: str) -> str:
    """Grade a student submission and provide feedback."""
    assignment = db.get_document('assignments', assignment_id)
    
    if not assignment:
        return f"❌ Assignment with ID {assignment_id} not found."
    
    word_count = len(submission_text.split())
    grade = min(100, max(60, 70 + (word_count // 50)))
    
    feedback = f"""
📝 Grade for {student_name} - {assignment['title']}
Score: {grade}/100
Status: {'Passed' if grade >= 70 else 'Needs Improvement'}

Feedback:
- Overall structure is good
- Main concepts are addressed
- Consider adding more examples and evidence
"""
    return feedback

teaching_agent = Agent(
    name="teaching_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction="""You are a Teaching Assistant Agent specialized in course management.
    Your responsibilities include:
    - Creating and managing assignments using create_assignment tool
    - Listing assignments for courses using list_assignments tool
    - Deleting assignments by ID using delete_assignment tool
    - Grading student submissions with helpful feedback using grade_submission tool
    
    Be professional, encouraging, and always confirm what you've done.
    When creating an assignment, always ask for course, title, due date, and points if not provided.""",
    tools=[create_assignment, list_assignments, delete_assignment, grade_submission],
)

# ============================================
# SUB-AGENT 2: CALENDAR AGENT
# ============================================

def schedule_office_hours(course: str, date: str, start_time: str, end_time: str) -> str:
    """Schedule office hours for a course."""
    meeting = {
        "type": "office_hours",
        "course": course,
        "date": date,
        "start_time": start_time,
        "end_time": end_time
    }
    db.save_task(meeting)
    return f"📅 Office hours scheduled for {course} on {date} from {start_time} to {end_time}"

def check_availability(date: str) -> str:
    """Check availability for a given date."""
    # Remove the strict 'type' filter to get all scheduled items for that date
    scheduled_items = db.query_documents('tasks', [('date', '==', date)])
    
    # Filter out standard to-do tasks, keeping only calendar events
    meetings = [item for item in scheduled_items if item.get('type') in ['office_hours', 'meeting']]
    
    if not meetings:
        return f"📆 Nothing scheduled for {date}. You're available."
    
    result = f"📆 Scheduled on {date}:\n"
    for m in meetings:
        if m['type'] == 'office_hours':
            result += f"  • {m['course']} office hours: {m['start_time']} - {m['end_time']}\n"
        elif m['type'] == 'meeting':
            result += f"  • Meeting: {m['title']} ({m['start_time']} - {m['end_time']})\n"
            
    return result

def schedule_meeting(title: str, date: str, start_time: str, end_time: str, attendees: List[str]) -> str:
    """Schedule a meeting."""
    meeting = {
        "type": "meeting",
        "title": title,
        "date": date,
        "start_time": start_time,
        "end_time": end_time,
        "attendees": attendees
    }
    db.save_task(meeting)
    return f"📅 Meeting '{title}' scheduled for {date} from {start_time} to {end_time} with {len(attendees)} attendees"

calendar_agent = Agent(
    name="calendar_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction="""You are a Calendar Assistant Agent specialized in schedule management.
    Your responsibilities include:
    - Scheduling office hours for courses using schedule_office_hours tool
    - Checking availability for dates using check_availability tool
    - Scheduling meetings with attendees using schedule_meeting tool
    
    Be efficient, clear, and always confirm schedule changes.
    When scheduling, ask for date, time, and duration if not provided.""",
    tools=[schedule_office_hours, check_availability, schedule_meeting],
)

# ============================================
# SUB-AGENT 3: TASK AGENT (with delete & clear all)
# ============================================

def add_task(title: str, priority: str = "medium", due_date: Optional[str] = None) -> str:
    """Add a new task to the todo list."""
    # Validate priority
    if priority not in ["high", "medium", "low"]:
        priority = "medium"
    
    task = {
        "type": "task",
        "title": title,
        "priority": priority,
        "due_date": due_date
    }
    saved = db.save_task(task)
    
    priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
    emoji = priority_emoji.get(priority, "📋")
    
    due_str = f" due {due_date}" if due_date else ""
    return f"{emoji} Task added: '{title}' (Priority: {priority}){due_str}. Task ID: {saved['id']}"

def list_tasks(show_completed: bool = False) -> str:
    """List all tasks, optionally including completed ones."""
    tasks = db.get_tasks(include_completed=show_completed)
    task_list = [t for t in tasks if t.get("type") == "task"]
    
    if not task_list:
        return "✅ No pending tasks! Great job!"
    
    result = "**📋 Your Tasks:**\n\n"
    for t in task_list:
        title = t.get("title", "Untitled Task / Old Calendar Event") 
        
        if t.get("completed"):
            result += f"- ✓ ~~{title}~~ *(ID: {t.get('id', 'unknown')})*\n"
        else:
            priority_mark = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(t.get("priority", "medium"), "⚪")
            due = f" **(Due: {t['due_date']})**" if t.get("due_date") else ""
            result += f"- {priority_mark} **{title}** *(ID: {t.get('id', 'unknown')})*{due}\n"
            
    return result

def complete_task(task_id: str) -> str:
    """Mark a task as completed."""
    task = db.update_task(task_id, {"completed": True})
    if task:
        return f"✅ Task '{task['title']}' marked as completed!"
    return f"❌ Task with ID {task_id} not found."

def delete_task(task_id: str) -> str:
    """Delete a task permanently by ID."""
    if db.delete_task(task_id):
        return f"🗑️ Task ID {task_id} has been permanently deleted."
    return f"❌ Task with ID {task_id} not found."

def clear_all_tasks(include_completed: bool = False) -> str:
    """Delete all tasks. Use include_completed=True to delete completed tasks too."""
    count = db.delete_all_tasks(include_completed=include_completed)
    
    if count == 0:
        return "📭 No tasks to delete."
    
    task_type = "all tasks (including completed)" if include_completed else "all pending tasks"
    return f"🗑️ Deleted {count} {task_type}."

def add_note(title: str, content: str, tags: Optional[List[str]] = None) -> str:
    """Add a note."""
    note = {
        "title": title,
        "content": content,
        "tags": tags or []
    }
    saved = db.save_note(note)
    return f"📝 Note '{title}' saved. Note ID: {saved['id']}"

def search_notes(query: str) -> str:
    """Search notes by keyword."""
    results = db.search_notes(query)
    if not results:
        return f"No notes found containing '{query}'."
    
    result = f"📚 Found {len(results)} note(s) containing '{query}':\n"
    for note in results:
        result += f"  • {note['title']}: {note['content'][:100]}...\n"
    return result

def delete_note(note_id: str) -> str:
    """Delete a note by ID."""
    if db.delete_note(note_id):
        return f"🗑️ Note ID {note_id} has been deleted."
    return f"❌ Note with ID {note_id} not found."

task_agent = Agent(
    name="task_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction="""You are a Task Management Assistant Agent specialized in helping teachers stay organized.
    Your responsibilities include:
    - Adding tasks with priorities and due dates using add_task tool
    - Listing tasks using list_tasks tool
    - Marking tasks as completed using complete_task tool
    - Deleting a specific task by ID using delete_task tool
    - Clearing ALL tasks at once using clear_all_tasks tool
    - Creating notes using add_note tool
    - Searching notes using search_notes tool
    - Deleting notes using delete_note tool
    - Showing database statistics using show_data_stats tool
    - Clearing all data using clear_all_data tool (use with caution)
    
    Be supportive, encouraging, and help the teacher stay productive.
    When adding a task, ask for priority and due date if not provided.
    
    IMPORTANT FORMATTING RULE: 
    When presenting lists, tasks, or statistics from your tools,
    ALWAYS preserve the line breaks and use Markdown bullet points. 
    NEVER squash the output into a single paragraph.
    
    IMPORTANT: 
    - Use delete_task for removing individual tasks
    - Use clear_all_tasks for removing multiple tasks at once
    - Use include_completed=True with clear_all_tasks to delete completed tasks too
    """,
    tools=[add_task, list_tasks, complete_task, delete_task, clear_all_tasks, 
           add_note, search_notes, delete_note, show_data_stats, clear_all_data],
)

# ============================================
# SUB-AGENT 4: SHIKSHAI AGENT
# ============================================

def generate_lesson(subject: str, grade: int, topic: str, language: str, full_content: str) -> str:
    """Save a fully generated lesson to the database.
    
    Args:
        subject: Subject name (Science, Math, History, etc.)
        grade: Grade level (1 to 16, where 16 = MSc)
        topic: Lesson topic
        language: Output language
        full_content: The complete lesson text (Explanation, Activity, Homework, etc.) to save.
    """
    # Validate grade range
    if not 1 <= grade <= 16:
        return f"❌ Invalid grade {grade}. Grade must be between 1 and 16 (16 = MSc)."
    
    # Check if lesson already exists
    existing_lessons = db.get_lessons(subject=subject, grade=grade)
    for lesson in existing_lessons:
        if lesson.get('topic', '').lower() == topic.lower():
            return f"📚 Lesson already exists! (ID: {lesson['id']})\nUse the 'read_lesson_plan' tool to view it."
    
    grade_display = "MSc" if grade == 16 else str(grade)
    
    # Save the COMPLETE lesson record with the actual text
    lesson = {
        "subject": subject,
        "grade": grade,
        "topic": topic,
        "language": language,
        "status": "generated",
        "full_content": full_content
    }
    
    saved = db.save_lesson(lesson)
    
    return f"✅ Success! The complete lesson on '{topic}' was saved to Firestore with ID: {saved['id']}"

def list_lessons(subject: Optional[str] = None, grade: Optional[int] = None) -> str:
    """List previously generated lessons."""
    lessons = db.get_lessons(subject, grade)
    
    if not lessons:
        return "📭 No lessons found. Generate one by saying: 'Generate lesson for Science, Grade 5, Topic Photosynthesis, Language English'"
    
    result = f"📚 **Found {len(lessons)} lesson(s):**\n\n"
    for lesson in lessons:
        grade_display = "MSc" if lesson.get('grade') == 16 else str(lesson.get('grade', '?'))
        result += f"**[{lesson['id']}]** {lesson['subject']} - Grade {grade_display}\n"
        result += f"   📖 {lesson['topic']} ({lesson.get('language', 'English')})\n"
        result += f"   💡 To read this: Ask me to 'Read lesson {lesson['id']}'\n\n"
    return result

def search_lessons(keyword: str) -> str:
    """Search lessons by keyword in topic or content."""
    results = db.search_lessons(keyword)
    
    if not results:
        return f"🔍 No lessons found containing '{keyword}'."
    
    result = f"🔍 **Found {len(results)} lesson(s) matching '{keyword}':**\n\n"
    for lesson in results:
        result += f"• [{lesson['id']}] {lesson['subject']}: {lesson['topic']} (Grade {lesson['grade']})\n"
    
    return result

def get_lesson_stats() -> str:
    """Get statistics about generated lessons."""
    stats = db.get_lesson_stats()
    
    if stats['total_lessons'] == 0:
        return "📊 No lessons generated yet. Create your first lesson using generate_lesson!"
    
    result = "📊 **LESSON DATABASE STATISTICS**\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    result += f"📚 Total Lessons: {stats['total_lessons']}\n\n"
    
    result += "**📖 By Subject:**\n"
    for subject, count in stats['by_subject'].items():
        result += f"   • {subject}: {count}\n"
    
    result += "\n**🎓 By Grade:**\n"
    for grade, count in stats['by_grade'].items():
        result += f"   • Grade {grade}: {count}\n"
    
    result += "\n**🌐 By Language:**\n"
    for language, count in stats['by_language'].items():
        result += f"   • {language}: {count}\n"
    
    result += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    return result

shiksha_agent = Agent(
    name="shiksha_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction="""You are **ShikshaAI** - A master teacher and lesson generator for Indian education.

## YOUR PERSONALITY
- Warm, encouraging, and patient
- Use Indian examples: mangoes, cricket, monsoon, Taj Mahal, Indian festivals
- Support ALL languages that Gemini supports

## YOUR CAPABILITIES

### 1. LESSON GENERATION
When a user asks to generate a lesson (Subject + Grade + Topic + Language):
1. FIRST, use your own intelligence to write out the complete, beautiful lesson plan (Explanation, Activity, Homework, Teacher Tip).
2. THEN, call the `generate_lesson` tool, passing your ENTIRE generated lesson text into the `full_content` parameter to save it to the database.
3. Finally, present the lesson to the user in the chat.

### 2. LESSON MANAGEMENT
- "List my lessons" → Use `list_lessons` tool
- "Search lessons for [keyword]" → Use `search_lessons` tool
- "Lesson statistics" → Use `get_lesson_stats` tool
- "Read lesson [ID]" → Use the `read_lesson_plan` tool to fetch and display the full saved text.

### 3. MCP DATA TOOLS (Your Superpowers!)
- "Show me India's education statistics" → Use `get_india_education_stats`
- "What's trending in education?" → Use `get_trending_education_topics`
- "Give me teaching insights" → Use `get_teaching_insights`
- "Compare India vs US education" → Use `compare_country_education`
- "Search for literacy rate data" → Use `search_education_indicator`

## IMPORTANT RULES:
- NEVER save a blank lesson. Always generate the text first, then pass it to the tool.
- Adapt explanation complexity to grade level (1-5 simple, 6-8 medium, 9-12 detailed, 13-16 advanced)
- When users ask for data/statistics, always use the MCP tools - that's your unique value!
""",
    tools=[
        generate_lesson, 
        list_lessons, 
        search_lessons, 
        get_lesson_stats,
        read_lesson_plan,  
        get_india_education_stats,
        get_trending_education_topics,
        get_teaching_insights,
        compare_country_education,
        search_education_indicator
    ],
)

# ============================================
# PRIMARY ORCHESTRATOR AGENT
# ============================================

root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction="""You are the **Primary Orchestrator Agent** for a University Teacher Assistant system.

## YOUR SUB-AGENTS:

1. **teaching_agent** - Assignments, grading, course management
2. **calendar_agent** - Office hours, meetings, schedules
3. **task_agent** - Tasks, todos, notes, reminders (includes delete & clear all)
4. **shiksha_agent** - Lesson generation, Q&A, multi-language, MCP-powered data tools

## HOW TO RESPOND TO CAPABILITY QUESTIONS:

When users ask "What can you do?", "Help me", "Capabilities", or similar:
→ FIRST, use the get_enhanced_capabilities() function from app.mcp_service.capabilities
→ This highlights your UNIQUE MCP superpowers (World Bank + Google Trends)
→ Always lead with MCP features before standard features

## HOW TO ROUTE:

| User Request | Send to |
|---------------|---------|
| "Show me India's education statistics" | shiksha_agent (MCP tool) |
| "What's trending in education?" | shiksha_agent (MCP tool) |
| "Compare India vs US education" | shiksha_agent (MCP tool) |
| "Give me teaching insights" | shiksha_agent (MCP tool) |
| "Create assignment..." / "Delete assignment..." | teaching_agent |
| "Schedule office hours..." | calendar_agent |
| "Add task..." / "Delete task..." / "Clear all tasks" | task_agent |
| "Generate lesson..." / "What is..." / "Explain..." | shiksha_agent |
| "List assignments" | teaching_agent |
| "Show tasks" | task_agent |
| "List lessons" | shiksha_agent |

## MULTI-STEP WORKFLOWS:

### MCP-Enhanced Workflows (NEW):
1. **Trend-based Lesson Creation:**
   - First: get_trending_education_topics() to see what students want
   - Then: generate_lesson() on that trending topic
   - Result: Timely, relevant lessons students actually want

2. **Data-Driven Assignment:**
   - First: get_india_education_stats() for real statistics
   - Then: create_assignment() using real data as examples
   - Result: Assignments with authentic, real-world data

3. **Comparative Analysis Workflow:**
   - First: compare_country_education() for multiple countries
   - Then: generate_lesson() on global education comparison
   - Result: Global perspective lessons

### Standard Workflows:
- First use teaching_agent for assignment, then task_agent for reminder
- Or use shiksha_agent for lesson, then task_agent to schedule teaching

## IMPORTANT RULES:

1. **Always highlight MCP features when users ask about capabilities**
2. **For generic questions like "What can you do?" → Use get_enhanced_capabilities()**
3. **For specific requests → Route to appropriate sub-agent**
4. **When users ask about "real data", "statistics", "trending" → Route to shiksha_agent MCP tools**
5. **Be enthusiastic about MCP integration - it's your unique value!**

## EXAMPLE RESPONSES:

**User: "What can you do?"**
→ Use get_enhanced_capabilities() to show MCP superpowers first

**User: "Help me"**  
→ "I can help you teach smarter with REAL data from World Bank and Google Trends! Here are some examples:..."

**User: "Show me India's stats"**
→ Route to shiksha_agent (get_india_education_stats)

**User: "Create assignment"**
→ Route to teaching_agent

Always be helpful, efficient, and clear. Show excitement about your MCP capabilities!
""",
    sub_agents=[teaching_agent, calendar_agent, task_agent, shiksha_agent],
)

# ============================================
# APP CREATION
# ============================================

app = App(
    root_agent=root_agent,
    name="app",
)

# For testing locally
if __name__ == "__main__":
    print("=" * 60)
    print("✅ TEACHER ASSISTANT SYSTEM WITH SHIKSHAI LOADED!")
    print("=" * 60)
    print(f"🤖 Model: gemini-2.5-flash")
    print(f"💾 Database: Google Cloud Firestore")
    print(f"\n🎯 SUB-AGENTS:")
    print(f"   1. teaching_agent - Assignments & Grading")
    print(f"   2. calendar_agent - Schedule & Meetings")
    print(f"   3. task_agent - Tasks, Notes & Reminders (Delete & Clear All)")
    print(f"   4. shiksha_agent - Lessons, Q&A (Multi-language)")
    print(f"\n🎛️ Orchestrator: root_agent")
    print(f"📱 App name: app")
    print("\n📝 EXAMPLE PROMPTS FOR ADK WEB:")
    print("-" * 40)
    print("📚 LESSONS:")
    print("   Generate lesson for Science, Grade 5, Topic Photosynthesis, Language Hindi")
    print("   List my lessons")
    print("   Search lessons for photosynthesis")
    print("   Lesson statistics")
    print("\n❓ QUESTIONS:")
    print("   What is gravity?")
    print("   प्रकाश संश्लेषण क्या है?")
    print("\n📋 ASSIGNMENTS:")
    print("   Create assignment for CS101: Python Quiz, due 2026-04-10, 50 points")
    print("   List all assignments")
    print("   Delete assignment 1")
    print("\n✅ TASKS (NEW DELETE & CLEAR ALL):")
    print("   Add high priority task: Grade quizzes due tomorrow")
    print("   List my tasks")
    print("   Complete task 1")
    print("   Delete task 2")
    print("   Clear all pending tasks")
    print("   Clear all tasks including completed")
    print("\n📝 NOTES:")
    print("   Add note: Meeting notes with content: Discussed syllabus")
    print("   Search notes for syllabus")
    print("   Delete note 1")
    print("\n📊 UTILITY:")
    print("   Show me database statistics")
    print("   Clear all data")
    print("\n📈 MCP DATA TOOLS (NEW!):")
    print("   Show me India's education statistics")
    print("   What's trending in education topics right now?")
    print("   Compare India vs China education spending")
    print("   Give me teaching insights based on latest data")
    print("=" * 60)
    print("\n🚀 To start server: make dev")
    print("💾 Data persists in Firestore (cloud storage)")