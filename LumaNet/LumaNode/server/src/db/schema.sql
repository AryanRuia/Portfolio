-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table with role-based access
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  username VARCHAR(50) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  role VARCHAR(20) CHECK (role IN ('admin', 'teacher', 'student')) NOT NULL,
  full_name VARCHAR(100),
  school_id UUID,
  created_at BIGINT NOT NULL,
  updated_at BIGINT NOT NULL,
  is_active BOOLEAN DEFAULT TRUE
);

-- Schools table
CREATE TABLE schools (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name VARCHAR(100) NOT NULL,
  created_at BIGINT NOT NULL
);

-- Subjects/Courses table
CREATE TABLE subjects (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name VARCHAR(100) NOT NULL,
  description TEXT,
  teacher_id UUID REFERENCES users(id),
  school_id UUID REFERENCES schools(id),
  created_at BIGINT NOT NULL,
  updated_at BIGINT NOT NULL,
  is_active BOOLEAN DEFAULT TRUE
);

-- Learning materials table
CREATE TABLE materials (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  subject_id UUID REFERENCES subjects(id) ON DELETE CASCADE,
  title VARCHAR(200) NOT NULL,
  filename VARCHAR(255) NOT NULL,
  file_size BIGINT,
  mime_type VARCHAR(100),
  storage_node VARCHAR(100) NOT NULL,
  created_at BIGINT NOT NULL,
  uploaded_by UUID REFERENCES users(id)
);

-- Student progress tracking
CREATE TABLE progress (
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  material_id UUID REFERENCES materials(id) ON DELETE CASCADE,
  completed BOOLEAN DEFAULT FALSE,
  completion_date BIGINT,
  updated_at BIGINT NOT NULL,
  PRIMARY KEY (user_id, material_id)
);

-- Sync events table (CRITICAL)
CREATE TABLE sync_events (
  id UUID PRIMARY KEY,
  event_type VARCHAR(50) NOT NULL,
  payload JSONB NOT NULL,
  timestamp BIGINT NOT NULL,
  source_node VARCHAR(100) NOT NULL,
  applied BOOLEAN DEFAULT FALSE,
  applied_at BIGINT,
  created_at BIGINT NOT NULL
);

-- Indexes for performance
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_subjects_teacher ON subjects(teacher_id);
CREATE INDEX idx_materials_subject ON materials(subject_id);
CREATE INDEX idx_sync_events_timestamp ON sync_events(timestamp);
CREATE INDEX idx_sync_events_source ON sync_events(source_node);
CREATE INDEX idx_sync_events_applied ON sync_events(applied);
