DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'link_shortener') THEN
    CREATE DATABASE link_shortener;
  END IF;
END
$$;