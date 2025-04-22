from flask import Blueprint, request, jsonify
from models.models import db, Reminder, CalendarEvent
from datetime import datetime

api = Blueprint('api', __name__)

# Reminder routes
@api.route('/reminders', methods=['GET'])
def get_reminders():
    reminders = Reminder.query.all()
    return jsonify([reminder.to_dict() for reminder in reminders])

@api.route('/reminders', methods=['POST'])
def create_reminder():
    data = request.get_json()
    
    try:
        due_date = datetime.fromisoformat(data['due_date'])
        reminder = Reminder(
            title=data['title'],
            description=data.get('description', ''),
            due_date=due_date,
            is_completed=data.get('is_completed', False)
        )
        
        db.session.add(reminder)
        db.session.commit()
        return jsonify(reminder.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@api.route('/reminders/<int:id>', methods=['PUT'])
def update_reminder(id):
    reminder = Reminder.query.get_or_404(id)
    data = request.get_json()
    
    try:
        if 'title' in data:
            reminder.title = data['title']
        if 'description' in data:
            reminder.description = data['description']
        if 'due_date' in data:
            reminder.due_date = datetime.fromisoformat(data['due_date'])
        if 'is_completed' in data:
            reminder.is_completed = data['is_completed']
        
        db.session.commit()
        return jsonify(reminder.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@api.route('/reminders/<int:id>', methods=['DELETE'])
def delete_reminder(id):
    reminder = Reminder.query.get_or_404(id)
    db.session.delete(reminder)
    db.session.commit()
    return '', 204

# Calendar event routes
@api.route('/calendar-events', methods=['GET'])
def get_calendar_events():
    events = CalendarEvent.query.all()
    return jsonify([event.to_dict() for event in events])

@api.route('/calendar-events', methods=['POST'])
def create_calendar_event():
    data = request.get_json()
    
    try:
        start_time = datetime.fromisoformat(data['start_time'])
        end_time = datetime.fromisoformat(data['end_time'])
        event = CalendarEvent(
            title=data['title'],
            description=data.get('description', ''),
            start_time=start_time,
            end_time=end_time,
            location=data.get('location', '')
        )
        
        db.session.add(event)
        db.session.commit()
        return jsonify(event.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@api.route('/calendar-events/<int:id>', methods=['PUT'])
def update_calendar_event(id):
    event = CalendarEvent.query.get_or_404(id)
    data = request.get_json()
    
    try:
        if 'title' in data:
            event.title = data['title']
        if 'description' in data:
            event.description = data['description']
        if 'start_time' in data:
            event.start_time = datetime.fromisoformat(data['start_time'])
        if 'end_time' in data:
            event.end_time = datetime.fromisoformat(data['end_time'])
        if 'location' in data:
            event.location = data['location']
        
        db.session.commit()
        return jsonify(event.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@api.route('/calendar-events/<int:id>', methods=['DELETE'])
def delete_calendar_event(id):
    event = CalendarEvent.query.get_or_404(id)
    db.session.delete(event)
    db.session.commit()
    return '', 204 