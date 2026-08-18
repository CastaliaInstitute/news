-- Add GoToSocial/Fediverse fields to faculty table
-- This allows faculty to post news articles under their own accounts

ALTER TABLE public.faculty 
ADD COLUMN IF NOT EXISTS gotosocial_handle text,
ADD COLUMN IF NOT EXISTS gotosocial_api_token text,
ADD COLUMN IF NOT EXISTS fediverse_enabled boolean DEFAULT false;

-- Add index for enabled faculty
CREATE INDEX IF NOT EXISTS idx_faculty_fediverse_enabled 
ON public.faculty(fediverse_enabled) 
WHERE fediverse_enabled = true;

-- Add comments
COMMENT ON COLUMN public.faculty.gotosocial_handle IS 
'Faculty GoToSocial/Mastodon handle (e.g., a.Tesla for https://social.castalia.institute/@a.Tesla)';

COMMENT ON COLUMN public.faculty.gotosocial_api_token IS 
'API token for posting to GoToSocial as this faculty member (encrypted at rest)';

COMMENT ON COLUMN public.faculty.fediverse_enabled IS 
'Whether this faculty member has fediverse posting enabled';

-- Example data (tokens would be real API tokens)
-- UPDATE faculty SET 
--   gotosocial_handle = 'a.Tesla',
--   fediverse_enabled = true,
--   gotosocial_api_token = 'actual_api_token_here'
-- WHERE slug = 'nikola-tesla';
