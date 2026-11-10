CREATE TABLE meta (key TEXT NOT NULL PRIMARY KEY, value TEXT NOT NULL);
-- key: schema_version ('1'), version ('2'), published_at ('2026-10-24T00:00:00Z')
CREATE TABLE rules (
  id TEXT NOT NULL PRIMARY KEY, position INTEGER NOT NULL, label TEXT NOT NULL,
  kind TEXT NOT NULL,            -- SignalKind enum name: FRAMEWORK, UI_TOOLKIT, LANGUAGE, BUILD_OPTIMIZATION, SDK
  category TEXT,                 -- SdkCategory enum name or NULL
  vendor TEXT, description TEXT, url TEXT,
  show_as_filter INTEGER NOT NULL -- 0 or 1
);
CREATE TABLE matchers (
  rule_id TEXT NOT NULL REFERENCES rules(id), position INTEGER NOT NULL,
  target TEXT NOT NULL,          -- NATIVE_LIB_NAME, ARCHIVE_PATH, COMPONENT_CLASS
  mode TEXT NOT NULL,            -- EXACT, PREFIX, REGEX
  pattern TEXT NOT NULL,
  PRIMARY KEY (rule_id, position)
);
CREATE TABLE version_tables (table_name TEXT NOT NULL, key TEXT NOT NULL, value TEXT NOT NULL, PRIMARY KEY (table_name, key));
