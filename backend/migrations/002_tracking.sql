-- 002: application tracking, documents, support, notifications
-- Extends 001_init.sql. Run after it.

CREATE TYPE llc_app_status AS ENUM (
  'not_started', 'submitted', 'processing', 'approved', 'completed', 'rejected'
);
CREATE TYPE ein_app_status AS ENUM (
  'pending', 'submitted', 'waiting_irs', 'received', 'completed'
);

CREATE TABLE llc_applications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES users(id),
  company_name TEXT NOT NULL,
  state TEXT NOT NULL DEFAULT 'Wyoming',
  status llc_app_status NOT NULL DEFAULT 'not_started',
  admin_notes TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE ein_applications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES users(id),
  llc_application_id UUID REFERENCES llc_applications(id),
  status ein_app_status NOT NULL DEFAULT 'pending',
  ein_number TEXT,
  admin_notes TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- documents/status_updates/messages/tickets/tasks/renewals/payments/subscriptions/audit_logs
-- already exist in 001_init.sql; messages.ticket_id is made a real FK here now
-- that tickets exists in the same migration set.
ALTER TABLE messages
  ADD CONSTRAINT fk_messages_ticket FOREIGN KEY (ticket_id) REFERENCES tickets(id) ON DELETE CASCADE;

CREATE TABLE notifications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  link TEXT,
  read_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_llc_apps_order_id ON llc_applications(order_id);
CREATE INDEX idx_ein_apps_order_id ON ein_applications(order_id);
CREATE INDEX idx_notifications_user_id ON notifications(user_id, read_at);
