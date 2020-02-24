--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.16
-- Dumped by pg_dump version 9.6.16

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

-- import gobs_on_import_change
CREATE TRIGGER gobs_on_import_change AFTER UPDATE ON gobs.import FOR EACH ROW EXECUTE PROCEDURE gobs.trg_after_import_validation();


-- indicator gobs_on_indicator_change
CREATE TRIGGER gobs_on_indicator_change AFTER INSERT OR UPDATE ON gobs.indicator FOR EACH ROW EXECUTE PROCEDURE gobs.trg_parse_indicator_paths();


--
-- PostgreSQL database dump complete
--

