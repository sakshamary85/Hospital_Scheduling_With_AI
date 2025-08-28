"""
Database Models for Hospital AI System
SQLAlchemy models for all entities
"""

from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, 
    ForeignKey, Text, Enum, JSON, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

Base = declarative_base()


class GenderEnum(enum.Enum):
    """Gender enumeration."""
    FEMALE = 0
    MALE = 1


class RiskLevelEnum(enum.Enum):
    """Risk level enumeration."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class AppointmentStatusEnum(enum.Enum):
    """Appointment status enumeration."""
    SCHEDULED = "SCHEDULED"
    CONFIRMED = "CONFIRMED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    NO_SHOW = "NO_SHOW"
    RESCHEDULED = "RESCHEDULED"


class SlotStatusEnum(enum.Enum):
    """Slot status enumeration."""
    AVAILABLE = "AVAILABLE"
    BOOKED = "BOOKED"
    RESERVED = "RESERVED"
    CANCELLED = "CANCELLED"


class Patient(Base):
    """Patient entity model."""
    
    __tablename__ = "patients"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String(50), unique=True, index=True, nullable=False)
    
    # Personal Information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True)
    phone = Column(String(20))
    date_of_birth = Column(DateTime)
    gender = Column(Enum(GenderEnum), nullable=False)
    
    # Medical Information
    age = Column(Integer)
    scholarship = Column(Boolean, default=False)
    hypertension = Column(Boolean, default=False)
    diabetes = Column(Boolean, default=False)
    alcoholism = Column(Boolean, default=False)
    handicap = Column(Boolean, default=False)
    
    # Address Information
    address = Column(Text)
    neighborhood = Column(String(100), index=True)
    city = Column(String(100))
    state = Column(String(100))
    postal_code = Column(String(20))
    
    # Communication Preferences
    sms_enabled = Column(Boolean, default=True)
    email_enabled = Column(Boolean, default=True)
    push_notifications_enabled = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    appointments = relationship("Appointment", back_populates="patient")
    medical_history = relationship("PatientMedicalHistory", back_populates="patient")
    
    # Indexes
    __table_args__ = (
        Index('idx_patient_neighborhood', 'neighborhood'),
        Index('idx_patient_gender_age', 'gender', 'age'),
    )


class Doctor(Base):
    """Doctor entity model."""
    
    __tablename__ = "doctors"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(String(50), unique=True, index=True, nullable=False)
    
    # Personal Information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True)
    phone = Column(String(20))
    
    # Professional Information
    specialization = Column(String(100))
    qualification = Column(String(100))
    experience_years = Column(Integer)
    license_number = Column(String(50), unique=True)
    
    # Working Schedule
    working_hours_start = Column(Integer, default=9)  # 9 AM
    working_hours_end = Column(Integer, default=18)  # 6 PM
    working_days = Column(JSON)  # ["Monday", "Tuesday", ...]
    
    # Status
    is_active = Column(Boolean, default=True)
    is_available = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    schedules = relationship("DoctorSchedule", back_populates="doctor")
    appointments = relationship("Appointment", back_populates="doctor")
    
    # Indexes
    __table_args__ = (
        Index('idx_doctor_specialization', 'specialization'),
        Index('idx_doctor_active', 'is_active', 'is_available'),
    )


class DoctorSchedule(Base):
    """Doctor schedule model."""
    
    __tablename__ = "doctor_schedules"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Keys
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    
    # Schedule Information
    date = Column(DateTime, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    slot_duration_minutes = Column(Integer, default=30)
    max_capacity = Column(Integer, default=1)
    
    # Status
    is_available = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    doctor = relationship("Doctor", back_populates="schedules")
    slots = relationship("TimeSlot", back_populates="schedule")
    
    # Indexes
    __table_args__ = (
        Index('idx_schedule_doctor_date', 'doctor_id', 'date'),
        Index('idx_schedule_available', 'is_available', 'date'),
    )


class TimeSlot(Base):
    """Time slot model."""
    
    __tablename__ = "time_slots"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Keys
    schedule_id = Column(Integer, ForeignKey("doctor_schedules.id"), nullable=False)
    
    # Slot Information
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(Enum(SlotStatusEnum), default=SlotStatusEnum.AVAILABLE)
    
    # Capacity
    max_capacity = Column(Integer, default=1)
    current_capacity = Column(Integer, default=0)
    
    # Buffer Time (for risk-based scheduling)
    buffer_time_minutes = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    schedule = relationship("DoctorSchedule", back_populates="slots")
    appointments = relationship("Appointment", back_populates="time_slot")
    
    # Indexes
    __table_args__ = (
        Index('idx_slot_schedule_time', 'schedule_id', 'start_time'),
        Index('idx_slot_status_time', 'status', 'start_time'),
        Index('idx_slot_available', 'status', 'current_capacity', 'max_capacity'),
    )


class Appointment(Base):
    """Appointment entity model."""
    
    __tablename__ = "appointments"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    appointment_id = Column(String(50), unique=True, index=True, nullable=False)
    
    # Foreign Keys
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    time_slot_id = Column(Integer, ForeignKey("time_slots.id"), nullable=False)
    
    # Appointment Information
    scheduled_date = Column(DateTime, nullable=False)
    appointment_date = Column(DateTime, nullable=False)
    status = Column(Enum(AppointmentStatusEnum), default=AppointmentStatusEnum.SCHEDULED)
    
    # ML Model Features
    lead_days = Column(Integer)  # Days between scheduling and appointment
    scheduled_day_of_week = Column(Integer)  # 0=Monday, 1=Tuesday, etc.
    scheduled_day_day = Column(Integer)  # Day of month
    appointment_day_day = Column(Integer)  # Day of month
    appointment_day_of_week = Column(Integer)  # 0=Monday, 1=Tuesday, etc.
    
    # Risk Assessment
    no_show_probability = Column(Float)
    risk_level = Column(Enum(RiskLevelEnum))
    buffer_time_minutes = Column(Integer, default=0)
    
    # Medical Information
    urgency_score = Column(Integer, default=1)  # 1-5 scale
    medical_notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")
    time_slot = relationship("TimeSlot", back_populates="appointments")
    
    # Indexes
    __table_args__ = (
        Index('idx_appointment_patient_date', 'patient_id', 'appointment_date'),
        Index('idx_appointment_doctor_date', 'doctor_id', 'appointment_date'),
        Index('idx_appointment_status_date', 'status', 'appointment_date'),
        Index('idx_appointment_risk', 'risk_level', 'no_show_probability'),
    )


class PatientMedicalHistory(Base):
    """Patient medical history model."""
    
    __tablename__ = "patient_medical_history"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Keys
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    
    # Historical Data
    no_show_rate = Column(Float, default=0.0)  # Historical no-show percentage
    last_show_status = Column(Boolean)  # True=showed up, False=no-show
    appointment_count = Column(Integer, default=0)  # Total appointments
    last_appointment_days = Column(Integer)  # Days since last appointment
    
    # Communication History
    sms_received_count = Column(Integer, default=0)
    email_sent_count = Column(Integer, default=0)
    reminder_response_rate = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    patient = relationship("Patient", back_populates="medical_history")
    
    # Indexes
    __table_args__ = (
        Index('idx_history_patient', 'patient_id'),
        Index('idx_history_no_show', 'no_show_rate'),
    )


class WaitlistEntry(Base):
    """Waitlist entry model."""
    
    __tablename__ = "waitlist_entries"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Keys
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    preferred_doctor_id = Column(Integer, ForeignKey("doctors.id"))
    
    # Waitlist Information
    priority_score = Column(Float, nullable=False)
    urgency_score = Column(Integer, default=1)
    preferred_date = Column(DateTime)
    preferred_time = Column(String(20))  # "morning", "afternoon", "evening"
    
    # Status
    is_active = Column(Boolean, default=True)
    assigned_appointment_id = Column(Integer, ForeignKey("appointments.id"))
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    patient = relationship("Patient")
    preferred_doctor = relationship("Doctor")
    assigned_appointment = relationship("Appointment")
    
    # Indexes
    __table_args__ = (
        Index('idx_waitlist_priority', 'priority_score'),
        Index('idx_waitlist_active', 'is_active', 'priority_score'),
        Index('idx_waitlist_patient', 'patient_id'),
    )


class NotificationLog(Base):
    """Notification log model."""
    
    __tablename__ = "notification_logs"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Keys
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    appointment_id = Column(Integer, ForeignKey("appointments.id"))
    
    # Notification Information
    notification_type = Column(String(50))  # "SMS", "EMAIL", "PUSH"
    status = Column(String(20))  # "SENT", "DELIVERED", "FAILED"
    message = Column(Text)
    
    # Timestamps
    sent_at = Column(DateTime, default=func.now())
    delivered_at = Column(DateTime)
    
    # Relationships
    patient = relationship("Patient")
    appointment = relationship("Appointment")
    
    # Indexes
    __table_args__ = (
        Index('idx_notification_patient', 'patient_id'),
        Index('idx_notification_appointment', 'appointment_id'),
        Index('idx_notification_type_status', 'notification_type', 'status'),
    )
