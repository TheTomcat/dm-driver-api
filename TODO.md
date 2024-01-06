# Longterm Feature Plan
 - [ ] Metadata in images - stuff that is visible but not user-modifiable - origin (cli, upload, web), colour details?
 - [ ] Image attribution (if known) - str field vs attribution table? Could also attribute entities 
 - [x] Image processing  - { palate: [(r,g,b), (r,g,b), (r,g,b)]} via color-thief maybe?
 - [ ] Asynchronous workers via Redis and Celery
 - [ ] Appropriate frontend for the above

# Fix Endpoint 
 - [ ] PATCH /image/{image_id}/tag?tag_id=x -> put tag_id into body
 - [ ] DELETE /image/{image_id}/tag?tag_id=x -> put tag_id into body
 - [ ] Ensure all endpoints rollback when an exception is raised 

# Add tests
 - [ ] combat ALL OF THE TESTS
 - [ ] combat POST a whole encounter in one go
 - [ ] images should return the full and thumbnail urls.
 - [ ] session needs extensive testing with respect to: GETting sessions in different modes, validation of fields etc
 - [x] images /image/{image_id}/full
 - [x] images /image/{image_id}/thumb
 - [x] images /image/{image_id}/b64
 - [x] images /image/random
 - [ ] messages /message/random
 - [ ] tags /tag/?q=something
 - [ ] messages /message/?q=something
 - [ ] For some unknown reason, the test suites for tagging images don't work. It works perfectly in prod. No idea why. 
 - [ ] models.Image create_from_uri needs a test
 - [ ] Check that when an image is deleted, it is "untagged", and conversely when a tag is deleted, images no longer are tagged

# Logic
 - [ ] Add filtering to image/random to allow, say, getting a random female character or a random ship backdrop
 - [ ] Fix participant.conditions mapping from "a,b,c" to ["a","b","c"]
 - [ ] Make a proper image hash function
 - [ ] Decide the best way to deal with thumbnails, if at all?
 - [ ] Endpoints should not return Response, should instead raise HTTPException
 - [ ] Implement marshaling of strings into json data for (e.g.) arbitrary metadata

# Types
 - [ ] Explicitly set response_model for all endpoints (Make the services return ORM models, and explicitly define response_model in the endpoints)
 
# Websockets
 - [x] Get the chatroom example working -> http://localhost:8000/live/
 - [x] Limit scope to allow multiple different chat rooms -> http://localhost:8000/live/{chatroom}
 - [x] Create some sort of pub/sub system to subscribe to events
 - [ ] Use the framework from that to manage sessions 

# Logging
 - [ ] Log server-side errors somewhere

# Authentication
 - [ ] Token based authentication, maybe
 - [ ] Rate limiting? Maybe for learning... https://github.com/alisaifee/limits https://snir-orlanczyk.medium.com/fastapi-rate-limit-middleware-ec9e46f84cdb
 
# Housekeeping
 - [ ] Move setup scripts that are specific to me into the import.py module