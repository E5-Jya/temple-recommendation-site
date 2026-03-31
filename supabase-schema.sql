-- ============================================================
-- Supabase schema for Thai Temple Database
-- Run this in the Supabase SQL Editor (Dashboard > SQL Editor)
-- ============================================================

-- 1. Create the temples table
CREATE TABLE IF NOT EXISTS temples (
  temple_id        TEXT PRIMARY KEY,
  name_th          TEXT NOT NULL,
  name_en          TEXT,
  place_type_th    TEXT,
  place_type_en    TEXT,
  slug             TEXT UNIQUE,
  tradition_th     TEXT,
  tradition_en     TEXT,
  abbot_th         TEXT,
  abbot_en         TEXT,
  founded_be       TEXT,
  founded_ce       TEXT,
  province_th      TEXT,
  province_en      TEXT,
  district_th      TEXT,
  district_en      TEXT,
  address_th       TEXT,
  website          TEXT,
  facebook_main    TEXT,
  facebook_en      TEXT,
  line_oa          TEXT,
  phone            TEXT,

  -- Activities (boolean-like, stored as text Y/N to match CSV)
  act_daily_meditation  TEXT DEFAULT 'N',
  act_dhamma_talk       TEXT DEFAULT 'N',
  act_lay_retreat       TEXT DEFAULT 'N',
  act_monk_ordination   TEXT DEFAULT 'N',
  act_novice_ordination TEXT DEFAULT 'N',
  act_white_robe        TEXT DEFAULT 'N',
  act_nun_program       TEXT DEFAULT 'N',
  act_annual_kathin     TEXT DEFAULT 'N',
  act_special_events    TEXT DEFAULT 'N',
  act_online_live       TEXT DEFAULT 'N',
  act_community_service TEXT DEFAULT 'N',

  -- Retreat info
  retreat_min_days      TEXT,
  retreat_cost          TEXT,
  retreat_booking_req   TEXT DEFAULT 'N',
  retreat_booking_channel TEXT,
  retreat_capacity      TEXT,

  -- Ordination info
  ord_min_days          TEXT,
  ord_cost              TEXT,
  ord_prerequisite      TEXT,

  -- Schedule
  sched_wake_time       TEXT,
  sched_morning_chant   TEXT,
  sched_meal_count      TEXT,
  sched_meal_type       TEXT,
  sched_evening_chant   TEXT,

  -- Descriptions
  blurb_th              TEXT,
  blurb_en              TEXT,

  -- Metadata
  last_updated          TEXT,
  data_sources          TEXT,
  notes                 TEXT,
  gmaps_place_id        TEXT,

  -- For Phase 3: track edit source
  last_edited_source    TEXT DEFAULT 'csv',
  updated_at            TIMESTAMPTZ DEFAULT now()
);

-- 2. Enable Row Level Security
ALTER TABLE temples ENABLE ROW LEVEL SECURITY;

-- 3. RLS Policy: anyone can read
CREATE POLICY "Public read access"
  ON temples FOR SELECT
  USING (true);

-- 4. RLS Policy: only authenticated users can update
--    (Phase 2 will further restrict to admin emails)
CREATE POLICY "Authenticated users can update"
  ON temples FOR UPDATE
  USING (auth.role() = 'authenticated');

-- 5. RLS Policy: service role can do everything (for CSV import)
CREATE POLICY "Service role full access"
  ON temples FOR ALL
  USING (auth.role() = 'service_role');

-- 6. Create index on slug for fast lookups
CREATE INDEX IF NOT EXISTS idx_temples_slug ON temples (slug);
CREATE INDEX IF NOT EXISTS idx_temples_province ON temples (province_en);
