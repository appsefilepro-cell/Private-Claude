"""
Calendar and Scheduling Integration
Manage coaching schedules, appointments, and reminders
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime, timedelta, time
from enum import Enum
import json
import uuid


class DayOfWeek(Enum):
    """Days of the week"""
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


class AppointmentStatus(Enum):
    """Appointment status"""
    AVAILABLE = "available"
    TENTATIVE = "tentative"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


@dataclass
class TimeSlot:
    """Available time slot for coaching"""
    day: DayOfWeek
    start_time: time
    end_time: time
    duration_minutes: int = 60


@dataclass
class CoachAvailability:
    """Coach's availability schedule"""
    coach_id: str

    # Regular availability
    weekly_schedule: Dict[DayOfWeek, List[TimeSlot]] = field(default_factory=dict)

    # Time off / blocked times
    blocked_dates: List[datetime] = field(default_factory=list)
    vacation_periods: List[Dict] = field(default_factory=list)  # {start_date, end_date, reason}

    # Scheduling preferences
    min_notice_hours: int = 24  # Minimum notice for booking
    max_advance_days: int = 90  # How far ahead clients can book
    buffer_between_sessions: int = 15  # Minutes between sessions
    max_sessions_per_day: int = 6

    # Session types and durations
    available_session_types: Dict[str, int] = field(default_factory=lambda: {
        "discovery": 30,
        "regular": 60,
        "intensive": 90,
        "emergency": 30
    })

    def add_availability(self, day: DayOfWeek, start_time: time, end_time: time):
        """Add availability for a specific day"""
        if day not in self.weekly_schedule:
            self.weekly_schedule[day] = []

        slot = TimeSlot(day=day, start_time=start_time, end_time=end_time)
        self.weekly_schedule[day].append(slot)

    def block_date(self, date: datetime, reason: str = "Blocked"):
        """Block a specific date"""
        self.blocked_dates.append(date)

    def add_vacation(self, start_date: datetime, end_date: datetime, reason: str = "Vacation"):
        """Add vacation period"""
        self.vacation_periods.append({
            'start_date': start_date,
            'end_date': end_date,
            'reason': reason
        })

    def is_available(self, date_time: datetime) -> bool:
        """Check if coach is available at specific date/time"""
        # Check if date is blocked
        if any(date_time.date() == blocked.date() for blocked in self.blocked_dates):
            return False

        # Check if in vacation period
        for vacation in self.vacation_periods:
            if vacation['start_date'].date() <= date_time.date() <= vacation['end_date'].date():
                return False

        # Check if within weekly schedule
        day_of_week = DayOfWeek(date_time.weekday())
        if day_of_week not in self.weekly_schedule:
            return False

        # Check if time falls within available slots
        time_only = date_time.time()
        for slot in self.weekly_schedule[day_of_week]:
            if slot.start_time <= time_only < slot.end_time:
                return True

        return False


@dataclass
class Appointment:
    """Coaching appointment"""
    appointment_id: str
    client_id: str
    client_name: str
    coach_id: str

    # Timing
    scheduled_datetime: datetime
    duration_minutes: int
    session_type: str

    # Status
    status: AppointmentStatus = AppointmentStatus.TENTATIVE

    # Details
    session_id: Optional[str] = None
    meeting_link: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None

    # Reminders
    reminder_sent: bool = False
    confirmation_sent: bool = False

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    @property
    def end_datetime(self) -> datetime:
        """Calculate end time of appointment"""
        return self.scheduled_datetime + timedelta(minutes=self.duration_minutes)

    def send_reminder(self) -> bool:
        """Mark reminder as sent"""
        self.reminder_sent = True
        self.updated_at = datetime.now()
        return True

    def confirm(self):
        """Confirm the appointment"""
        self.status = AppointmentStatus.CONFIRMED
        self.confirmation_sent = True
        self.updated_at = datetime.now()

    def cancel(self, reason: str = ""):
        """Cancel the appointment"""
        self.status = AppointmentStatus.CANCELLED
        if reason:
            self.notes = f"Cancelled: {reason}"
        self.updated_at = datetime.now()

    def complete(self):
        """Mark appointment as completed"""
        self.status = AppointmentStatus.COMPLETED
        self.updated_at = datetime.now()


class CalendarManager:
    """
    Manages coaching calendar, appointments, and scheduling
    """

    def __init__(self, storage_path: str = "data/calendar.json"):
        self.storage_path = storage_path
        self.appointments: Dict[str, Appointment] = {}
        self.availability: Optional[CoachAvailability] = None
        self.load_calendar()

    def set_availability(self, coach_id: str):
        """Initialize coach availability"""
        self.availability = CoachAvailability(coach_id=coach_id)

    def book_appointment(self,
                        client_id: str,
                        client_name: str,
                        coach_id: str,
                        scheduled_datetime: datetime,
                        duration_minutes: int = 60,
                        session_type: str = "regular") -> Optional[Appointment]:
        """Book a new appointment"""

        # Check if time slot is available
        if self.availability and not self.availability.is_available(scheduled_datetime):
            return None

        # Check for conflicts
        if self.has_conflict(scheduled_datetime, duration_minutes):
            return None

        appointment_id = str(uuid.uuid4())

        appointment = Appointment(
            appointment_id=appointment_id,
            client_id=client_id,
            client_name=client_name,
            coach_id=coach_id,
            scheduled_datetime=scheduled_datetime,
            duration_minutes=duration_minutes,
            session_type=session_type
        )

        self.appointments[appointment_id] = appointment
        self.save_calendar()

        return appointment

    def has_conflict(self, scheduled_datetime: datetime, duration_minutes: int) -> bool:
        """Check if there's a scheduling conflict"""
        proposed_end = scheduled_datetime + timedelta(minutes=duration_minutes)

        for appointment in self.appointments.values():
            if appointment.status in [AppointmentStatus.CANCELLED]:
                continue

            existing_end = appointment.end_datetime

            # Check for overlap
            if (scheduled_datetime < existing_end and
                proposed_end > appointment.scheduled_datetime):
                return True

        return False

    def get_appointment(self, appointment_id: str) -> Optional[Appointment]:
        """Get a specific appointment"""
        return self.appointments.get(appointment_id)

    def get_client_appointments(self, client_id: str) -> List[Appointment]:
        """Get all appointments for a client"""
        appointments = [
            apt for apt in self.appointments.values()
            if apt.client_id == client_id
        ]
        return sorted(appointments, key=lambda a: a.scheduled_datetime)

    def get_upcoming_appointments(self, days_ahead: int = 7) -> List[Appointment]:
        """Get upcoming appointments"""
        now = datetime.now()
        future = now + timedelta(days=days_ahead)

        upcoming = [
            apt for apt in self.appointments.values()
            if (apt.status in [AppointmentStatus.TENTATIVE, AppointmentStatus.CONFIRMED] and
                now <= apt.scheduled_datetime <= future)
        ]

        return sorted(upcoming, key=lambda a: a.scheduled_datetime)

    def get_todays_appointments(self) -> List[Appointment]:
        """Get today's appointments"""
        today = datetime.now().date()

        todays = [
            apt for apt in self.appointments.values()
            if (apt.scheduled_datetime.date() == today and
                apt.status not in [AppointmentStatus.CANCELLED])
        ]

        return sorted(todays, key=lambda a: a.scheduled_datetime)

    def get_available_slots(self,
                           start_date: datetime,
                           end_date: datetime,
                           duration_minutes: int = 60) -> List[datetime]:
        """Find available time slots in a date range"""
        if not self.availability:
            return []

        available_slots = []
        current_date = start_date

        while current_date <= end_date:
            # Check each day
            day_of_week = DayOfWeek(current_date.weekday())

            if day_of_week in self.availability.weekly_schedule:
                for slot in self.availability.weekly_schedule[day_of_week]:
                    # Generate potential appointment times
                    slot_datetime = datetime.combine(current_date.date(), slot.start_time)

                    # Check if slot is long enough and available
                    while slot_datetime.time() < slot.end_time:
                        if (self.availability.is_available(slot_datetime) and
                            not self.has_conflict(slot_datetime, duration_minutes)):
                            available_slots.append(slot_datetime)

                        slot_datetime += timedelta(minutes=duration_minutes)

            current_date += timedelta(days=1)

        return available_slots

    def reschedule_appointment(self,
                              appointment_id: str,
                              new_datetime: datetime) -> bool:
        """Reschedule an appointment"""
        appointment = self.get_appointment(appointment_id)
        if not appointment:
            return False

        # Check if new time is available
        if self.has_conflict(new_datetime, appointment.duration_minutes):
            return False

        appointment.scheduled_datetime = new_datetime
        appointment.status = AppointmentStatus.TENTATIVE
        appointment.updated_at = datetime.now()

        self.save_calendar()
        return True

    def get_appointments_needing_reminder(self, hours_before: int = 24) -> List[Appointment]:
        """Get appointments that need reminders sent"""
        reminder_time = datetime.now() + timedelta(hours=hours_before)

        return [
            apt for apt in self.appointments.values()
            if (not apt.reminder_sent and
                apt.status == AppointmentStatus.CONFIRMED and
                apt.scheduled_datetime <= reminder_time)
        ]

    def get_calendar_summary(self, days: int = 7) -> Dict:
        """Get calendar summary"""
        upcoming = self.get_upcoming_appointments(days)
        today = self.get_todays_appointments()

        return {
            'appointments_today': len(today),
            'appointments_this_week': len(upcoming),
            'confirmed': len([a for a in upcoming if a.status == AppointmentStatus.CONFIRMED]),
            'tentative': len([a for a in upcoming if a.status == AppointmentStatus.TENTATIVE]),
            'next_appointment': upcoming[0] if upcoming else None,
            'reminders_needed': len(self.get_appointments_needing_reminder())
        }

    def generate_schedule(self, date: datetime) -> str:
        """Generate daily schedule"""
        day_appointments = [
            apt for apt in self.appointments.values()
            if (apt.scheduled_datetime.date() == date.date() and
                apt.status not in [AppointmentStatus.CANCELLED])
        ]

        if not day_appointments:
            return f"No appointments scheduled for {date.strftime('%B %d, %Y')}"

        day_appointments.sort(key=lambda a: a.scheduled_datetime)

        schedule = f"SCHEDULE FOR {date.strftime('%A, %B %d, %Y')}\n"
        schedule += "=" * 50 + "\n\n"

        for apt in day_appointments:
            time_str = apt.scheduled_datetime.strftime('%I:%M %p')
            end_str = apt.end_datetime.strftime('%I:%M %p')
            status_str = apt.status.value.upper()

            schedule += f"{time_str} - {end_str} | {apt.client_name}\n"
            schedule += f"  Type: {apt.session_type} ({apt.duration_minutes} min)\n"
            schedule += f"  Status: {status_str}\n"

            if apt.meeting_link:
                schedule += f"  Link: {apt.meeting_link}\n"

            schedule += "\n"

        return schedule

    def save_calendar(self):
        """Save calendar data"""
        import os
        os.makedirs(os.path.dirname(self.storage_path) if os.path.dirname(self.storage_path) else '.', exist_ok=True)

        data = {
            'appointments': {
                apt_id: {
                    **apt.__dict__,
                    'scheduled_datetime': apt.scheduled_datetime.isoformat(),
                    'created_at': apt.created_at.isoformat(),
                    'updated_at': apt.updated_at.isoformat(),
                    'status': apt.status.value
                }
                for apt_id, apt in self.appointments.items()
            }
        }

        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)

    def load_calendar(self):
        """Load calendar data"""
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
                self.appointments = {}
        except FileNotFoundError:
            self.appointments = {}
