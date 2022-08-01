--
-- PostgreSQL database dump
--

-- Dumped from database version 13.7 (Debian 13.7-1.pgdg110+1)
-- Dumped by pg_dump version 13.7 (Debian 13.7-1.pgdg110+1)

SET statement_timeout = 0;
SET lock_timeout = 0;

SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;

SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

-- import gobs_on_import_change
CREATE TRIGGER gobs_on_import_change AFTER UPDATE ON gobs.import FOR EACH ROW EXECUTE PROCEDURE gobs.trg_after_import_validation();


-- indicator gobs_on_indicator_change
CREATE TRIGGER gobs_on_indicator_change AFTER INSERT OR UPDATE ON gobs.indicator FOR EACH ROW EXECUTE PROCEDURE gobs.trg_parse_indicator_paths();


-- observation trg_log_deleted_object
CREATE TRIGGER trg_log_deleted_object AFTER DELETE ON gobs.observation FOR EACH ROW EXECUTE PROCEDURE gobs.log_deleted_object();


-- document trg_manage_object_timestamps
CREATE TRIGGER trg_manage_object_timestamps BEFORE INSERT OR UPDATE ON gobs.document FOR EACH ROW EXECUTE PROCEDURE gobs.manage_object_timestamps();


-- indicator trg_manage_object_timestamps
CREATE TRIGGER trg_manage_object_timestamps BEFORE INSERT OR UPDATE ON gobs.indicator FOR EACH ROW EXECUTE PROCEDURE gobs.manage_object_timestamps();


-- observation trg_manage_object_timestamps
CREATE TRIGGER trg_manage_object_timestamps BEFORE INSERT OR UPDATE ON gobs.observation FOR EACH ROW EXECUTE PROCEDURE gobs.manage_object_timestamps();


-- spatial_object trg_manage_object_timestamps
CREATE TRIGGER trg_manage_object_timestamps BEFORE INSERT OR UPDATE ON gobs.spatial_object FOR EACH ROW EXECUTE PROCEDURE gobs.manage_object_timestamps();


-- spatial_object trg_update_observation_on_spatial_object_change
CREATE TRIGGER trg_update_observation_on_spatial_object_change AFTER UPDATE ON gobs.spatial_object FOR EACH ROW EXECUTE PROCEDURE gobs.update_observation_on_spatial_object_change();


-- spatial_object trg_update_spatial_object_end_validity
CREATE TRIGGER trg_update_spatial_object_end_validity AFTER INSERT ON gobs.spatial_object FOR EACH ROW EXECUTE PROCEDURE gobs.update_spatial_object_end_validity();


--
-- PostgreSQL database dump complete
--

